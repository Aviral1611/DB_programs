package com.demo.vault.util;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;

/**
 * AES-128 Encryption Utility.
 * Encrypts plaintext passwords into unreadable ciphertext before they reach the database.
 * Decrypts ciphertext back into plaintext when the user requests their password.
 *
 * IMPORTANT: In a production environment, the secret key would NEVER be hardcoded.
 * It would be stored in an environment variable, a secrets manager (like AWS KMS),
 * or a hardware security module (HSM).
 */
public class AESEncryptor {

    private static final String ALGORITHM = "AES";

    // A fixed 16-byte (128-bit) key for demo purposes.
    // In production, this would come from an environment variable or vault.
    private static final byte[] FIXED_KEY = "DemoSecretKey128".getBytes();
    private static final SecretKeySpec SECRET_KEY = new SecretKeySpec(FIXED_KEY, ALGORITHM);

    /**
     * Encrypts a plaintext string using AES-128.
     * Returns a Base64-encoded string safe for database storage.
     *
     * @param plainText The password in readable format
     * @return Base64-encoded encrypted string
     * @throws Exception if encryption fails
     */
    public static String encrypt(String plainText) throws Exception {
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        cipher.init(Cipher.ENCRYPT_MODE, SECRET_KEY);
        byte[] encryptedBytes = cipher.doFinal(plainText.getBytes("UTF-8"));
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }

    /**
     * Decrypts a Base64-encoded AES ciphertext back to plaintext.
     *
     * @param cipherText The Base64-encoded encrypted string from the database
     * @return The original password in readable format
     * @throws Exception if decryption fails (e.g., wrong key, corrupted data)
     */
    public static String decrypt(String cipherText) throws Exception {
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        cipher.init(Cipher.DECRYPT_MODE, SECRET_KEY);
        byte[] decodedBytes = Base64.getDecoder().decode(cipherText);
        byte[] decryptedBytes = cipher.doFinal(decodedBytes);
        return new String(decryptedBytes, "UTF-8");
    }
}
