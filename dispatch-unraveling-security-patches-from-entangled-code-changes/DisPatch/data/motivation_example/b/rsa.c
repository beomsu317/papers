int RSA_padding_check_PKCS1_OAEP_mgf1(unsigned char *to, int tlen, const unsigned char *from, int flen, int num, const unsigned char *param, int plen, const EVP_MD *md, const EVP_MD *mgf1md)
{
    int i, dblen = 0, mlen = -1, one_index = 0, msg_index;
    unsigned int good, found_one_byte;
    const unsigned char *maskedseed, *maskeddb;
    unsigned char *db = NULL, *em = NULL, seed[EVP_MAX_MD_SIZE],
        phash[EVP_MAX_MD_SIZE];
    int mdlen;
    if (md == NULL)
        md = EVP_sha1();
    if (mgf1md == NULL)
        mgf1md = md;
    mdlen = EVP_MD_size(md);
    if (tlen <= 0 || flen <= 0)
        return -1;
    if (num < flen || num < 2 * mdlen + 2)
        goto decoding_err;
    dblen = num - mdlen - 1;
    db = OPENSSL_malloc(dblen);
    if (db == NULL) {
        RSAerr(RSA_F_RSA_PADDING_CHECK_PKCS1_OAEP_MGF1, ERR_R_MALLOC_FAILURE);
        goto cleanup;
    }
    em = OPENSSL_zalloc(num);
    if (em == NULL) {
        RSAerr(RSA_F_RSA_PADDING_CHECK_PKCS1_OAEP_MGF1,ERR_R_MALLOC_FAILURE);
        goto cleanup;
    }
    good = constant_time_is_zero(from[0]);
    maskedseed = from + 1;
    maskeddb = from + 1 + mdlen;
    if (PKCS1_MGF1(seed, mdlen, maskeddb, dblen, mgf1md))
        goto cleanup;
    for (i = 0; i < mdlen; i++)
        seed[i] ^= maskedseed[i];
    if (PKCS1_MGF1(db, dblen, seed, mdlen, mgf1md))
        goto cleanup;
    for (i = 0; i < dblen; i++)
        db[i] ^= maskeddb[i];

    if (!EVP_Digest((void *)param, plen, phash, NULL, md, NULL))
        goto cleanup;
    good &= constant_time_is_zero(CRYPTO_memcmp(db, phash, mdlen));
    found_one_byte = 0;
    for (i = mdlen; i < dblen; i++) {
        unsigned int equals1 = constant_time_eq(db[i], 1);
        unsigned int equals0 = constant_time_is_zero(db[i]);
        one_index = constant_time_select_int(~found_one_byte & equals1,i, one_index);
        found_one_byte |= equals1;
        good &= (found_one_byte | equals0);
    }
    good &= found_one_byte;
    if (!good)
        goto decoding_err;
    msg_index = one_index + 1;
    mlen = dblen - msg_index;
    if (tlen < mlen) {
        RSAerr(RSA_F_RSA_PADDING_CHECK_PKCS1_OAEP_MGF1, RSA_R_DATA_TOO_LARGE);
        mlen = -1;
    } else {
        memcpy(to, db + msg_index, mlen);
        goto cleanup;
    }
 decoding_err:
    RSAerr(RSA_F_RSA_PADDING_CHECK_PKCS1_OAEP_MGF1,
           RSA_R_OAEP_DECODING_ERROR);
 cleanup:
    OPENSSL_cleanse(seed, sizeof(seed));
    OPENSSL_clear_free(db, dblen);
    OPENSSL_clear_free(em, num);
    return mlen;
}