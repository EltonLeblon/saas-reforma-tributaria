import streamlit_authenticator as stauth

# Na versão nova, primeiro criamos o objeto e depois passamos as senhas para o método
senhas = ['123', '456']
hashes = stauth.Hasher.hash_passwords(senhas)

print("--- COPIE OS HASHES ABAIXO ---")
for senha, hash_gerado in zip(senhas, hashes):
    print(f"Senha: {senha} -> Hash: {hash_gerado}")