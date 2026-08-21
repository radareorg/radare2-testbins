#include <jni.h>
#include <stdarg.h>

JNIEXPORT jint JNICALL Java_JNISlots_direct(JNIEnv *env, jobject receiver) {
	return (*env)->GetVersion (env);
}

JNIEXPORT jint JNICALL Java_JNISlots_copied(JNIEnv *env, jobject receiver) {
	JNIEnv *copy = env;
	return (*copy)->GetVersion (copy);
}

JNIEXPORT jint JNICALL Java_JNISlots_spilled(JNIEnv *env, jobject receiver) {
	JNIEnv *saved = env;
	return (*saved)->GetVersion (saved);
}

JNIEXPORT jint JNICALL Java_JNISlots_variadic(JNIEnv *env, jobject receiver, jmethodID method) {
	return (*env)->CallIntMethod (env, receiver, method, 42);
}

JNIEXPORT jint JNICALL Java_JNISlots_vaList(JNIEnv *env, jobject receiver, jmethodID method, ...) {
	va_list args;
	va_start (args, method);
	jint result = (*env)->CallIntMethodV (
		env, receiver, method, args);
	va_end (args);
	return result;
}

JNIEXPORT jint JNICALL Java_JNISlots_array(JNIEnv *env, jobject receiver, jmethodID method) {
	jvalue args[1] = {{ .i = 42 }};
	return (*env)->CallIntMethodA (
		env, receiver, method, args);
}

JNIEXPORT void JNICALL Java_JNISlots_buffers(JNIEnv *env, jobject receiver, jobject first, jobject second, jobject third) {
	(*env)->GetDirectBufferAddress (env, first);
	(*env)->GetDirectBufferAddress (env, second);
	(*env)->GetDirectBufferAddress (env, third);
}
