/*
 * This software is Copyright (c) 2017 Dhiru Kholia, Copyright (c) 2017
 * Frederic Heem, Copyright (c) 2013 Lukas Odzioba <ukasz at openwall dot net>,
 * and it is hereby released to the general public under the following terms:
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted.
 */
#ifdef HAVE_OPENCL

#if FMT_EXTERNS_H
extern struct fmt_main fmt_opencl_ethereum_presale;
#elif FMT_REGISTERS_H
john_register_one(&fmt_opencl_ethereum_presale);
#else

#include <string.h>

#include "misc.h"
#include "arch.h"
#include "common.h"
#include "formats.h"
#include "options.h"
#include "../run/opencl/opencl_pbkdf2_hmac_sha256.h"
#include "ethereum_common.h"
#include "opencl_common.h"

#define FORMAT_NAME             "Ethereum Presale Wallet"
#define FORMAT_LABEL            "ethereum-presale-opencl"
#define ALGORITHM_NAME          "PBKDF2-SHA256 AES Keccak OpenCL"
#define BENCHMARK_COMMENT       ""
#define BENCHMARK_LENGTH        7
#define MIN_KEYS_PER_CRYPT      1
#define MAX_KEYS_PER_CRYPT      1
#define BINARY_ALIGN            sizeof(uint32_t)
#define SALT_SIZE               sizeof(*cur_salt)
#define SALT_ALIGN              sizeof(int)
#define PLAINTEXT_LENGTH        55
#define KERNEL_NAME             "ethereum_presale_init"
#define SPLIT_KERNEL_NAME       "pbkdf2_sha256_loop"
#define PRESALE_KERNEL_NAME     "ethereum_presale_process"

#define HASH_LOOPS              (2*2*5*5*5) // factors 2 2 2 2 5 5 5
#define ITERATIONS              2000

struct fmt_tests opencl_ethereum_presale_tests[] = {
	// "real-world" presale wallet, thanks to @FredericHeem, https://github.com/tagawa/website/blob/master/pyethtool/pyethtool.py#L61
	{"$ethereum$w*0b2fa2c63a8b5603e1104fbada15a609aa9736ed41db1678d91a9b1a1f7c1628e711dbc250c4c289b06b0faa56cd499dc4af9daf878202db22cc61df1a91c918314c77ce92e5c8b1265580edd79a852acf40fe2138653ac16524c08247381d9802cf5ef3f8c4baf69fb869f2b7fb796bae853cfbdc3c5b788a14e75f39e0cf7df2e90779181a5dd45cce8e8df938af3c6b6c8a92ce123338e6ed87eb16ff11a02cd4a2a07aff8a3a57097fcf137501e07a941a7ce9bc19498252d98769125fbd2c9a14f1c56212a6bf2a7e374474c60e7a3a1cf443ce8194c4c960474472d6ca761ada075169fa8c7017bf1274b99df898deb65f51ed8eb29fbc0997d69c9800ad9b8351155bec5d8e7f73e7e2882a6e1b62883d0158c44fed8e4412fb18e75757e1355aaadd8a2dab50ae40c800d032dc77d3e84904085d628b5a13b60317d6f12ede26b7b38e7c6805bea1d2e11e3a7d7153b76ebfd99ae2536dfdd071ff8111a86fbd63e7b17155162263ef45471ac5b4c517520572cd19410cc4cbde77914fad12326fe5a4cbd5fc4a297740d6b5e64001196b0531e2464b7e4cee77136a38844b94dc59a9a72eec3ff49bca3d5bf0c29652ee6ff028e22f8936aac58fa3cf05ce4c8de8883204e43b57e4ebed922ad7b3a8953042033d34d7e94bc8ff393d1df4c8b062f5228b4f9dbc5d157af96772af1ef2c84f6562049b1c44f0359c07f193623a8b0f1b7e34b31481ddf54a24128e5a21b929f57fd07f8911ad8eb8d8bfe928ae9dfa2d35663764161094552a43b43a0a43dca687d4d04b79c8dbb2d4f87b7d8e0805a77adddfd5149741faa594009639fb730dccfbee1f99286aaf94052c06a1c68efc29dcd57a8b1a421e*f9438b7121a15fd127ec0d8a72ee2b3e8da04a5a*74fdb879ece341dd590a769f2cd39d67", "password"},
	// presale wallets with 'bkp' generated by old https://github.com/ethereum/pyethsaletool
	{"$ethereum$w*9ace195a18b83b09da933f60f64fb4651e8413a5fdc12249724088d43dcd6d3c943f83d78d475e61177ca38965cb7794a2e1225250ae29134e60492871c79bf2*b9cfc3e87d22f37be858f97944844efbd32e5da5*ec97af5d7e240a559ee74f7a9e7312f2", "openwall"},
	{"$ethereum$w*4ab35fcb5c3101af70d5b3bf22829af3dbd48813273b17566ee364285c7bcfb2d52611a58e54d3e6be27e458073304e71e356afc4c97da0143910308f30563fe*c4dfdaa5288b477d0ff25a260ef32a24282cc4e2*97b3d2c2c8106507b87744f0b12f73c2", "password12345"},
	{NULL}
};

// input
typedef struct {
	salt_t pbkdf2;
	uint8_t encseed[1024];
	uint32_t eslen;
} ethereum_salt_t;

// output
typedef struct {
	uint8_t hash[16];
} hash_t;

static int new_keys;

static pass_t *host_pass;
static ethereum_salt_t *host_salt;
static hash_t *hash_out;
static unsigned hash_size;
static cl_int cl_error;
static cl_mem mem_in, mem_pbkdf2_out, mem_out, mem_salt, mem_state;
static cl_kernel split_kernel, decrypt_kernel;
static struct fmt_main *self;

static custom_salt *cur_salt;

#define STEP			0
#define SEED			1024

static const char *warn[] = {
        "xfer: ",  ", init: " , ", crypt: ", ", decrypt: ", ", res xfer: "
};

static int split_events[] = { 2, -1, -1 };

// This file contains auto-tuning routine(s). Has to be included after formats definitions.
#include "opencl_autotune.h"

static void release_clobj(void);

static void create_clobj(size_t kpc, struct fmt_main *self)
{
	release_clobj();

#define CL_RO CL_MEM_READ_ONLY
#define CL_WO CL_MEM_WRITE_ONLY
#define CL_RW CL_MEM_READ_WRITE

#define CLCREATEBUFFER(_flags, _size, _string)\
	clCreateBuffer(context[gpu_id], _flags, _size, NULL, &cl_error); \
	HANDLE_CLERROR(cl_error, _string);

#define CLKERNELARG(kernel, id, arg)\
	HANDLE_CLERROR(clSetKernelArg(kernel, id, sizeof(arg), &arg), \
	               "Error setting kernel arg");

	host_pass = mem_calloc(kpc, sizeof(pass_t));
	host_salt = mem_calloc(1, sizeof(ethereum_salt_t));
	hash_size = kpc * sizeof(hash_t);
	hash_out = mem_calloc(hash_size, 1);

	mem_in = CLCREATEBUFFER(CL_RO, kpc * sizeof(pass_t),
	                        "Cannot allocate mem in");
	mem_salt = CLCREATEBUFFER(CL_RO, sizeof(ethereum_salt_t),
	                          "Cannot allocate mem salt");
	mem_pbkdf2_out = CLCREATEBUFFER(CL_RW, kpc * sizeof(crack_t),
	                                "Cannot allocate mem pbkdf2_out");
	mem_out = CLCREATEBUFFER(CL_WO, hash_size,
	                         "Cannot allocate mem out");
	mem_state = CLCREATEBUFFER(CL_RW, kpc * sizeof(state_t),
	                           "Cannot allocate mem state");

	CLKERNELARG(crypt_kernel, 0, mem_in);
	CLKERNELARG(crypt_kernel, 1, mem_salt);
	CLKERNELARG(crypt_kernel, 2, mem_state);

	CLKERNELARG(split_kernel, 0, mem_state);

	CLKERNELARG(decrypt_kernel, 0, mem_pbkdf2_out);
	CLKERNELARG(decrypt_kernel, 1, mem_salt);
	CLKERNELARG(decrypt_kernel, 2, mem_state);
	CLKERNELARG(decrypt_kernel, 3, mem_out);
}

/* ------- Helper functions ------- */
static size_t get_task_max_work_group_size()
{
	size_t s;

	s = autotune_get_task_max_work_group_size(FALSE, 0, crypt_kernel);
	s = MIN(s, autotune_get_task_max_work_group_size(FALSE, 0, split_kernel));
	return s;
}

static void release_clobj(void)
{
	if (host_salt) {
		HANDLE_CLERROR(clReleaseMemObject(mem_in), "Release mem in");
		HANDLE_CLERROR(clReleaseMemObject(mem_salt), "Release mem salt");
		HANDLE_CLERROR(clReleaseMemObject(mem_pbkdf2_out), "Release pbkdf2out");
		HANDLE_CLERROR(clReleaseMemObject(mem_out), "Release mem out");
		HANDLE_CLERROR(clReleaseMemObject(mem_state), "Release mem state");

		MEM_FREE(host_pass);
		MEM_FREE(host_salt);
	}
}

static void init(struct fmt_main *_self)
{
	self = _self;
	opencl_prepare_dev(gpu_id);
}

static void reset(struct db_main *db)
{
	if (!program[gpu_id]) {
		char build_opts[128];

		snprintf(build_opts, sizeof(build_opts),
		         "-DHASH_LOOPS=%u -DPLAINTEXT_LENGTH=%u -DPRESALE",
		         HASH_LOOPS, PLAINTEXT_LENGTH);
		opencl_init("$JOHN/opencl/ethereum_kernel.cl",
		            gpu_id, build_opts);

		crypt_kernel =
			clCreateKernel(program[gpu_id], KERNEL_NAME, &cl_error);
		HANDLE_CLERROR(cl_error, "Error creating crypt kernel");

		split_kernel =
			clCreateKernel(program[gpu_id], SPLIT_KERNEL_NAME, &cl_error);
		HANDLE_CLERROR(cl_error, "Error creating split kernel");

		decrypt_kernel =
			clCreateKernel(program[gpu_id], PRESALE_KERNEL_NAME, &cl_error);
		HANDLE_CLERROR(cl_error, "Error creating decrypt kernel");
	}

	// Initialize openCL tuning (library) for this format.
	opencl_init_auto_setup(SEED, HASH_LOOPS, split_events, warn,
	                       2, self, create_clobj, release_clobj,
	                       sizeof(state_t), 0, db);

	// Auto tune execution from shared/included code.
	autotune_run(self, ITERATIONS, 0, 200);
}

static void done(void)
{
	if (program[gpu_id]) {
		release_clobj();
		HANDLE_CLERROR(clReleaseKernel(crypt_kernel), "Release kernel 1");
		HANDLE_CLERROR(clReleaseKernel(split_kernel), "Release kernel 2");
		HANDLE_CLERROR(clReleaseKernel(decrypt_kernel), "Release kernel 3");
		HANDLE_CLERROR(clReleaseProgram(program[gpu_id]),
		               "Release Program");

		program[gpu_id] = NULL;
	}
}

static int ethereum_valid(char *ciphertext, struct fmt_main *self)
{
	char *ctcopy, *keeptr, *p;
	int extra;

	if (strncmp(ciphertext, FORMAT_TAG, TAG_LENGTH) != 0)
		return 0;

	ctcopy = xstrdup(ciphertext);
	keeptr = ctcopy;

	ctcopy += TAG_LENGTH;
	if ((p = strtokm(ctcopy, "*")) == NULL) // type
		goto err;
	if (*p != 'w')
		goto err;
	if (*p == 'w') {
		if ((p = strtokm(NULL, "*")) == NULL)   // encseed
			goto err;
		if (hexlenl(p, &extra) >= 1024 * 2 || extra)
			goto err;
		if ((p = strtokm(NULL, "*")) == NULL)   // ethaddr
			goto err;
		if (hexlenl(p, &extra) > 128 || extra)
			goto err;
		if ((p = strtokm(NULL, "*")) == NULL)   // bkp
			goto err;
		if (hexlenl(p, &extra) != 32 || extra)
			goto err;
	}

	MEM_FREE(keeptr);
	return 1;

err:
	MEM_FREE(keeptr);
	return 0;
}

static void set_salt(void *salt)
{
	cur_salt = (custom_salt*)salt;

	memcpy(host_salt->encseed, cur_salt->encseed, cur_salt->eslen);
	host_salt->eslen = cur_salt->eslen;

	HANDLE_CLERROR(clEnqueueWriteBuffer(queue[gpu_id], mem_salt,
		CL_FALSE, 0, sizeof(ethereum_salt_t), host_salt, 0, NULL, NULL),
	    "Salt transfer");
	HANDLE_CLERROR(clFlush(queue[gpu_id]), "clFlush failed in set_salt()");
}

static int crypt_all(int *pcount, struct db_salt *salt)
{
	static int keys_done;
	int i;
	const int count = *pcount;
	int loops = (2000 + HASH_LOOPS - 1) / HASH_LOOPS;
	size_t *lws = local_work_size ? &local_work_size : NULL;

	global_work_size = GET_NEXT_MULTIPLE(count, local_work_size);

	if (new_keys || global_work_size > keys_done) {
		// Copy data to gpu
		BENCH_CLERROR(clEnqueueWriteBuffer(queue[gpu_id], mem_in,
			CL_FALSE, 0, global_work_size * sizeof(pass_t), host_pass, 0,
			NULL, multi_profilingEvent[0]), "Copy data to gpu");

		// Run kernel
		BENCH_CLERROR(clEnqueueNDRangeKernel(queue[gpu_id], crypt_kernel,
			1, NULL, &global_work_size, lws, 0, NULL, multi_profilingEvent[1]), "Run kernel");

		for (i = 0; i < (ocl_autotune_running ? 1 : loops); i++) {
			BENCH_CLERROR(clEnqueueNDRangeKernel(queue[gpu_id], split_kernel,
				1, NULL, &global_work_size, lws, 0, NULL, multi_profilingEvent[2]), "Run split kernel");
			BENCH_CLERROR(clFinish(queue[gpu_id]), "clFinish");
			opencl_process_event();
		}
		keys_done = global_work_size;
		new_keys = 0;
	}

	// Run decrypt kernel
	BENCH_CLERROR(clEnqueueNDRangeKernel(queue[gpu_id], decrypt_kernel,
		1, NULL, &global_work_size, lws, 0, NULL, multi_profilingEvent[3]), "Run kernel");

	// Read the result back
	BENCH_CLERROR(clEnqueueReadBuffer(queue[gpu_id], mem_out,
		CL_TRUE, 0, hash_size, hash_out, 0,
		NULL, multi_profilingEvent[4]), "Copy result back");

	return count;
}

static int cmp_all(void *binary, int count)
{
	int index;

	for (index = 0; index < count; index++)
		if (!memcmp(binary, hash_out[index].hash, ARCH_SIZE))
			return 1;
	return 0;
}

static int cmp_one(void *binary, int index)
{
	return !memcmp(binary, hash_out[index].hash, BINARY_SIZE);
}

static int cmp_exact(char *source, int index)
{
	return 1;
}

static void set_key(char *key, int index)
{
	int saved_len = MIN(strlen(key), PLAINTEXT_LENGTH);

	memcpy(host_pass[index].v, key, saved_len);
	host_pass[index].length = saved_len;
	new_keys = 1;
}

static char *get_key(int index)
{
	static char ret[PLAINTEXT_LENGTH + 1];
	memcpy(ret, host_pass[index].v, PLAINTEXT_LENGTH);
	ret[host_pass[index].length] = 0;
	return ret;
}

struct fmt_main fmt_opencl_ethereum_presale = {
	{
		FORMAT_LABEL,
		FORMAT_NAME,
		ALGORITHM_NAME,
		BENCHMARK_COMMENT,
		BENCHMARK_LENGTH,
		0,
		PLAINTEXT_LENGTH,
		BINARY_SIZE,
		BINARY_ALIGN,
		SALT_SIZE,
		SALT_ALIGN,
		MIN_KEYS_PER_CRYPT,
		MAX_KEYS_PER_CRYPT,
		FMT_CASE | FMT_8_BIT | FMT_HUGE_INPUT,
		{
			"iteration count",
		},
		{ FORMAT_TAG },
		opencl_ethereum_presale_tests
	}, {
		init,
		done,
		reset,
		fmt_default_prepare,
		ethereum_valid,
		fmt_default_split,
		ethereum_get_binary,
		ethereum_common_get_salt,
		{
			ethereum_common_iteration_count,
		},
		fmt_default_source,
		{
			fmt_default_binary_hash
		},
		fmt_default_salt_hash,
		NULL,
		set_salt,
		set_key,
		get_key,
		fmt_default_clear_keys,
		crypt_all,
		{
			fmt_default_get_hash  // required due to usage of FMT_HUGE_INPUT
		},
		cmp_all,
		cmp_one,
		cmp_exact
	}
};

#endif /* plugin stanza */

#endif /* HAVE_OPENCL */
