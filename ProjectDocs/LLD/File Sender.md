**What will it do?**

Docker container which tracks changes to a pre-configured directory such as file creation, file update or file deletion. Once change is detected, it will start process flow as per configuration

Request:


| API    | Type | Payload                                                                                                                 | Response                                                                                                    |
| ------ | ---- | ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| upload | POST | {"chunks":[{"id":"c1","size_in_KB":120},{"id":"c2","size_in_KB":200},{"id":"c3","size_in_KB":610}],"request_id":"1234"} | {"chunks":[{"id":"c1","send":"OK"},{"id":"c2","send":"NOTOK"},{"id":"c3","send":"OK"}],"request_id":"1234"} |
|        |      |                                                                                                                         |                                                                                                             |


**Open Points**

- Uses "something" to observe new file in a pre-configured directory
	- what if a file is uploaded few levels inside the parent folder
- If new file is determined and located, break the file into chunks and send to target peers
	- how many chunks? what's chunk size
	- how to pick target peer?
	- how to make sure chunks of a file are evenly spread across peers such that all chunks don't land up in one target peer
	- how to make sure the chunks also gets replicated saving us from target peer failure or unavailability
- Encryption of chunks before sending such that only file owner can decrypt it later
- How to ssh segments(or one whole chunk) such that these segments can be combined by target peer File Receiver.



Notes: 

==Query==: 
i have a requirement and looking for solution. i want to encrypt a file and store it in remote storage server. And when i fetch this file i should be able to decrypt it. Only i should be able to encrypt and decrypt the file. what are my options? using symmetric key with passphrase, or asymmetric key with passphrase? Then if i change my passphrase (in passphrase rotation) how can i retrieve files which were loaded with old passphrase?

==Answer==:

You've got a common and important requirement for secure file storage! Let's break down your options, their implications, and the crucial aspect of passphrase rotation.

### Understanding Symmetric vs. Asymmetric Encryption for Files

**1. Symmetric Key Encryption (e.g., AES-256)**

- **How it works:** Uses a single key for both encryption and decryption.1 This key is typically derived from your passphrase.
    
- **Pros:**
    
    - **Faster:** Much faster than asymmetric encryption for large files.2
        
    - **Simpler:** Generally easier to implement and manage.
        
    - **Strong:** Algorithms like AES-256 are extremely secure when implemented correctly with a strong key and good practices (like using an Initialization Vector - IV).3
        
- **Cons:**
    
    - **Key Distribution/Management:** The single biggest challenge is securely managing and distributing the symmetric key (or the passphrase that derives it).4 If someone gets your key/passphrase, they can decrypt everything.
        
    - **Passphrase is the Key:** Your passphrase _is_ the key (or used to derive it). If you forget it, your data is lost.
        
- **Best for:** Encrypting bulk data (files), where the same person or entity needs to encrypt and decrypt. This is the most common and practical choice for individual file encryption.
    

**2. Asymmetric Key Encryption (e.g., RSA, ECC)**

- **How it works:** Uses a pair of mathematically linked keys: a **public key** for encryption and a **private key** for decryption.5 You share your public key, but keep your private key secret.6
    
- **Pros:**
    
    - **Key Distribution:** Solves the key distribution problem.7 Anyone can encrypt for you with your public key, but only you (with your private key) can decrypt.8
        
    - **Authentication/Digital Signatures:** The private key can also be used to create digital signatures, proving you authored a file.9
        
- **Cons:**
    
    - **Slower:** Significantly slower, especially for large amounts of data. Not practical for encrypting entire files.
        
    - **Complexity:** More complex to implement and manage.
        
    - **Private Key Security:** Your private key is paramount. If it's compromised, your security is breached. It also needs to be protected with a strong passphrase.
        
- **Best for:** Secure communication (encrypting a session key), digital signatures, and encrypting small amounts of data (like a symmetric key).
    

### Your Options for File Encryption:

Given your requirement ("Only I should be able to encrypt and decrypt the file"), **symmetric key encryption (e.g., AES-256) is almost certainly the correct choice for the file content itself.**

You will typically use a process like this:


1. **Generate a Data Encryption Key (DEK):** A random, strong symmetric key (e.g., 256-bit AES key). This key will actually encrypt your file.
    
2. **Derive a Key Encryption Key (KEK) from your passphrase:** Use a **Key Derivation Function (KDF)** like PBKDF2 or scrypt with a strong passphrase, a unique salt, and many iterations. This KEK is used to encrypt your DEK.
    
3. **Encrypt the File:** Use the DEK to encrypt your file.
    
4. **Encrypt the DEK:** Use the KEK (derived from your passphrase) to encrypt the DEK
    
5. **Store:** Store the encrypted file, the encrypted DEK, and the salt (for the KDF) together on the remote storage. The IV used for file encryption also needs to be stored, usually alongside the encrypted data.
    

**Decryption Process:**

1. **Retrieve:** Fetch the encrypted file, encrypted DEK, salt, and IV from remote storage.
    
2. **Derive KEK:** Use your passphrase and the stored salt with the same KDF to re-derive the KEK.
    
3. **Decrypt DEK:** Use the re-derived KEK to decrypt the encrypted DEK, revealing the original DEK
    
4. **Decrypt File:** Use the decrypted DEK and the stored IV to decrypt the file.
    

### Passphrase Rotation: The Challenge and Solutions

This is where it gets tricky with symmetric encryption, as your passphrase is tied to the decryption process.

**Problem:** If you directly encrypt the DEK with a KEK derived from "Old Passphrase," and then you change your passphrase to "New Passphrase" and derive a "New KEK," the "New KEK" cannot decrypt the DEK encrypted with the "Old KEK."

**Solutions for Passphrase Rotation:**

The core idea is to re-encrypt the DEK with the new passphrase. You don't need to re-encrypt the entire large file.

**Option 1: Re-encrypting the Data Encryption Key (DEK) for each file (Recommended)**

This is the most robust and standard approach.

1. **Retrieve File Metadata:** When you want to change your passphrase, for each encrypted file, you retrieve its encrypted DEK and salt from storage.
    
2. **Decrypt DEK with Old Passphrase:** Use your _old_ passphrase and the file's associated salt to derive the "Old KEK" and decrypt the DEK.
    
3. **Derive New KEK with New Passphrase:** Get your _new_ passphrase. Generate a _new_ random salt for the new passphrase. Use the new passphrase and the new salt with your KDF to derive the "New KEK."
    
4. **Encrypt DEK with New Passphrase:** Encrypt the _already decrypted_ DEK using the "New KEK."
    
5. **Update Metadata:** Store the newly encrypted DEK and the _new_ salt (important!) back with the file on the remote server, replacing the old ones. The file content itself remains unchanged.
    

**How to Retrieve Files Encrypted with Old Passphrase (During Rotation):**

During the rotation process, you'll need _both_ your old passphrase (to decrypt the existing DEKs) and your new passphrase (to re-encrypt them). Once all files' DEKs have been re-encrypted, the old passphrase is no longer needed.

**Example Process (Conceptual):**

```
For each_encrypted_file_on_server:
    Fetch (encrypted_DEK_old, salt_old, encrypted_file_content, IV)

    # Step 1: Decrypt DEK using old passphrase
    KEK_old = KDF(old_passphrase, salt_old)
    DEK = decrypt(encrypted_DEK_old, KEK_old)

    # Step 2: Generate new salt and re-encrypt DEK using new passphrase
    salt_new = generate_new_random_salt()
    KEK_new = KDF(new_passphrase, salt_new)
    encrypted_DEK_new = encrypt(DEK, KEK_new)

    # Step 3: Update metadata on server
    Store (encrypted_DEK_new, salt_new, encrypted_file_content, IV) on server
```

**Option 2: Key Wrapping (More complex, but robust for many keys)**

This approach is more common in complex Key Management Systems (KMS). You would have a master **Key Encryption Key (KEK)** that is stored and protected by your passphrase. This KEK then encrypts _all_ your DEKs.

1. **Master KEK:** Your passphrase derives this master KEK.
    
2. **File DEKs:** Each file has its own unique DEK
    
3. **Encryption:** Encrypt each file with its unique DEK. Then, encrypt each DEK with the master KEK. Store (encrypted file, encrypted DEK, IV) for each file.
    
4. **Passphrase Rotation:** When you rotate your passphrase, you simply decrypt your _single_ master KEK (using the old passphrase), and then re-encrypt _that single master KEK_ with your new passphrase. The DEKs for the files remain untouched, as they are wrapped by the master KEK, not directly by the passphrase.
    

**How to Retrieve Files Encrypted with Old Passphrase (During Rotation with Key Wrapping):**

You don't need to re-touch individual files. You only need to rotate the protection around your _single_ master KEK. After rotation, you use the new passphrase to get the new master KEK, which can still decrypt all the DEKs because the DEKs themselves didn't change, only the key that encrypts the master KEK.

**Pros of Key Wrapping for Rotation:**

- Only one key (the master KEK) needs to be re-wrapped/re-encrypted when the passphrase changes. This is efficient if you have many files.
    

**Cons of Key Wrapping for Rotation:**

- Adds a layer of complexity (managing a master KEK).
    
- The security of all files now depends on the security of this single master KEK.
    

### Example Libraries/Tools in Python:

You would primarily use the `cryptography` library for this.

- `cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC`: For deriving keys from passphrases.
    
- `cryptography.hazmat.primitives.ciphers`: For AES encryption (e.g., `Cipher`, `modes.GCM` or `modes.CBC` with an `unpadder`). AES in GCM mode is generally preferred as it provides authenticated encryption (protects against tampering).13
    
- `cryptography.fernet`: A high-level symmetric encryption primitive that handles many details for you (like IVs, salts, and authentication tags) but might be less flexible for your specific passphrase rotation needs if you want to swap the KEK directly. It's built on AES-GCM and PBKDF2, so understanding its components is useful.
    

**Practical Implementation Hints:**

- **Salt:** Always use a unique, randomly generated salt for each encryption operation where a passphrase derives a key. Store this salt openly with the encrypted data. It's not secret, but crucial for security.
    
- **Initialization Vector (IV):** For block ciphers like AES, an IV is required. It must be unique for each encryption with the same key. Store it openly with the encrypted data. It's not secret.
    
- **Authenticated Encryption:** Use a mode like AES-GCM. This adds an authentication tag to the ciphertext, allowing you to detect if the encrypted data has been tampered with.
    
- **Key Storage:** When you decrypt the DEK with your passphrase, hold it in memory only for as long as needed, and consider attempting to zero out the memory afterwards (though Python's GC makes this hard to guarantee).
    

For your requirement, **symmetric key encryption (AES-256) for the file content, with the Data Encryption Key (DEK) protected by a Key Encryption Key (KEK) derived from your passphrase (via PBKDF2 with a salt), is the way to go.** When rotating the passphrase, you'll need to fetch each file's encrypted DEK, decrypt it with the old passphrase, generate a _new salt_ for the _new passphrase_, re-encrypt the DEK with the new passphrase (and new KEK), and update the stored encrypted DEK and new salt on your remote storage.


--------------------------------------------------------------
==Query==: i like second option of 'Key Wrapping'. can you check and confirm my understanding of 'Key Wrapping'?

1. Ask user to enter passphrase and salt if it's not configured for this user. Let's call generated key as 'user_key' If master kek doesn't exists then create one, let's call it 'master_kek' and encrypt with 'user_key'. Also encrypt the text 'key_is_correct' with 'user_key'. we will use it for future validation of passphrase and salt.

2. if configured, ask user for passphrase and salt , and generate user_kek. Now decrypt encryption of 'key_is_correct' with 'user_kek'. if the decrypted value is 'key_is_correct' then it means user entered correct passphrase and salt. If not, entered passphrase or salt is incorrect.

If user entered passphrase and salt is correct, then it proceeds with following encryption process 

a. Generate DEK and IV to encrypt the file. Encrypt the file using DEK and IV

b. Decrypt 'master_kek' using 'user_kek'

c. use decrypted 'master_kek' to encrypt DEK

d. store IV and encrypted DEK in safe place

e. Encrypted file is ready to be stored in remote storage

3. Decryption Process is as follows:

a. Ask user for passphrase and salt. Get 'user_kek' using passphrase and salt. Check this 'user_key' against previously encrypted phrase 'key_is_correct'. If it matches then it means passphrase and salt are correct

b. Use 'user_kek' to decrypt 'master_kek'. 

c. Use 'master_kek' to decrypt DEK. Now use decrypted DEK and IV to decrypt the file.

==Answer==: Your understanding of Key Wrapping (Option 2) is very good, and you've accurately captured the core concepts! Let's go through it step-by-step and confirm, adding some nuances and best practices for a real-world implementation.

### Confirmation and Nuances of Your Key Wrapping Understanding:

**1. Initial Setup (First Time User/No Configuration):**

- **"Ask user to enter passphrase and salt if it's not configured for this user."**
    
    - **Passphrase:** Yes, absolutely.
        
    - **Salt:** No, the user should **not** enter the salt. The salt should be **randomly generated** for each KDF derivation and stored **alongside** the encrypted `master_kek` (and the encrypted `key_is_correct` validation string). The salt's purpose is to make KDF outputs unique even for the same passphrase, and it is not secret.
        
- **"Let's call generated key as 'user_key'"**
    
    - Correct. This is your **Key Encryption Key (KEK)** derived from the passphrase + salt. Let's call it `passphrase_derived_KEK` for clarity.
        
- **"If master kek doesn't exists then create one, let's call it 'master_kek' and encrypt with 'user_key'."**
    
    - Correct. Generate a strong, random `master_kek` (e.g., 256-bit AES key). Encrypt this `master_kek` using the `passphrase_derived_KEK`. Store this `encrypted_master_kek` (along with the salt used to derive `passphrase_derived_KEK`).
        
- **"Also encrypt the text 'key_is_correct' with 'user_key'. we will use it for future validation of passphrase and salt."**
    
    - Correct and a very good practice! This is often called a "login test" or "password verification string." Encrypt a known plaintext (like `'key_is_correct'`) with your `passphrase_derived_KEK`. Store this `encrypted_validation_string` (along with the salt used to derive `passphrase_derived_KEK` for this specific string, if different, though usually it's the same salt as for the `master_kek`).
        

**2. Subsequent Access / Passphrase Validation:**

- **"if configured, ask user for passphrase and salt , and generate user_kek."**
    
    - Yes, ask for passphrase.
        
    - **Salt:** Retrieve the **stored salt** (the one saved with the `encrypted_validation_string`) and use it with the user's entered passphrase to derive the `passphrase_derived_KEK`. The user doesn't enter the salt here.
        
- **"Now decrypt encryption of 'key_is_correct' with 'user_kek'. if the decrypted value is 'key_is_correct' then it means user entered correct passphrase and salt. If not, entered passphrase or salt is incorrect."**
    
    - Perfect. This is the standard way to validate a passphrase without storing the passphrase itself. You'll also need the IV that was used to encrypt `'key_is_correct'`.
        
- **If user entered passphrase and salt is correct, then it proceeds with following encryption process:**
    
    - **"a. Generate DEK and IV to encrypt the file. Encrypt the file using DEK and IV"**
        
        - Correct. Each file gets a fresh, random DEK and IV.
            
    - **"b. Decrypt 'master_kek' using 'user_kek'"**
        
        - Correct. You retrieve the `encrypted_master_kek` (and its associated salt) from storage, derive the `passphrase_derived_KEK` using the correct passphrase and this salt, and then decrypt the `encrypted_master_kek` to get the plain `master_kek`.
            
    - **"c. use decrypted 'master_kek' to encrypt DEK"**
        
        - Correct. This is the "wrapping" step. You'll need an IV here too for encrypting the DEK. Since DEKs are small, a non-predictable IV (e.g., random) is fine. This encrypted DEK is often called the "wrapped DEK."
            
    - **"d. store IV and encrypted DEK in safe place"**
        
        - Correct. These (the file's IV, and the wrapped DEK + its IV) are the metadata needed for decryption and should be stored alongside the encrypted file on the remote server.
            
    - **"e. Encrypted file is ready to be stored in remote storage"**
        
        - Correct.
            

**3. Decryption Process:**

- **"a. Ask user for passphrase and salt. Get 'user_kek' using passphrase and salt. Check this 'user_key' against previously encrypted phrase 'key_is_correct'. If it matches then it means passphrase and salt are correct"**
    
    - Yes, this is the first validation step. Retrieve the `encrypted_validation_string` and its salt, derive `passphrase_derived_KEK`, decrypt the validation string.
        
- **"b. Use 'user_kek' to decrypt 'master_kek'."**
    
    - Correct. Retrieve the `encrypted_master_kek` and its associated salt. Use your `passphrase_derived_KEK` to decrypt it.
        
- **"c. Use 'master_kek' to decrypt DEK. Now use decrypted DEK and IV to decrypt the file."**
    
    - Correct. Retrieve the `wrapped DEK` and its IV from the file's metadata. Use the decrypted `master_kek` to unwrap the DEK. Finally, use the unwrapped DEK and the file's IV to decrypt the actual file content.
        

### Passphrase Rotation with Key Wrapping:

Your understanding of the rotation benefit is also correct.

- **No need to re-encrypt files:** When you change your passphrase, you **do not** need to re-encrypt any of your files.
    
- **The Rotation Process:**
    
    1. **Ask for Old Passphrase:** Prompt the user for their _current_ (old) passphrase.
        
    2. **Validate Old Passphrase:** Use the validation string method (step 2 from above) to confirm the old passphrase is correct.
        
    3. **Decrypt Master KEK:** Use the correct old passphrase and its associated salt to derive the `passphrase_derived_KEK_old`. Use this to decrypt the `encrypted_master_kek` to get the plain `master_kek`.
        
    4. **Ask for New Passphrase:** Prompt the user for their _new_ passphrase.
        
    5. **Generate New Salt:** Generate a **new, random salt** for this new passphrase.
        
    6. **Derive New KEK:** Use the new passphrase and the new salt with your KDF to derive `passphrase_derived_KEK_new`.
        
    7. **Encrypt Master KEK with New KEK:** Re-encrypt the _plain_ `master_kek` (obtained in step 3) using `passphrase_derived_KEK_new`.
        
    8. **Update Stored Data:** Store the `newly_encrypted_master_kek` and the **new salt** (for this new passphrase) in your configuration. Also, re-encrypt your validation string with the `passphrase_derived_KEK_new` and store the `newly_encrypted_validation_string` and its associated (new) salt.
        
    9. **Old Passphrase no longer needed:** Once this process is complete, the old passphrase (and its associated salt) are no longer required.
        

This "Key Wrapping" approach is indeed very elegant for passphrase rotation, as it means only a tiny amount of data (the `master_kek` and the validation string) needs to be re-encrypted, not all your large files.

Excellent plan!