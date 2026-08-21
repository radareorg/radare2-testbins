#include <jni.h>

// R2R test/db/anal/jni

static jobject native_overloaded_array(JNIEnv *env, jobject receiver,
		jintArray values, jstring name) {
	(void)env;
	(void)receiver;
	(void)values;
	return name;
}

static jint native_overloaded_int(JNIEnv *env, jobject receiver) {
	(void)env;
	(void)receiver;
	return 42;
}

JNIEXPORT jlong exact_native(JNIEnv *env, jobject receiver, jlong value) {
	(void)env;
	(void)receiver;
	return value;
}

__attribute__((used, visibility("hidden")))
const JNINativeMethod jni_test_methods[] = {
	{
		"overloaded",
		"([ILjava/lang/String;)Ljava/lang/Object;",
		(void *)native_overloaded_array,
	},
	{
		"overloaded",
		"()I",
		(void *)native_overloaded_int,
	},
	{
		"exact",
		"(J)J",
		(void *)exact_native,
	},
};

JNIEXPORT jint JNI_OnLoad(JavaVM *vm, void *reserved) {
	(void)vm;
	(void)reserved;
	return JNI_VERSION_1_6;
}
