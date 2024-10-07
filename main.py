import tkinter as tk
from tkinter import messagebox
import time

# IP/IP-1
IP = [2, 6, 3, 1, 4, 8, 5, 7]
IP_INV = [4, 1, 3, 5, 7, 2, 8, 6]

# P10/P8
P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
P8 = [6, 3, 7, 4, 8, 5, 10, 9]

# EP
EP = [4, 1, 2, 3, 2, 3, 4, 1]

# S-boxes
S1 = [[1, 0, 3, 2], [3, 2, 1, 0], [0, 2, 1, 3], [3, 1, 0, 2]]
S2 = [[0, 1, 2, 3], [2, 3, 1, 0], [3, 0, 1, 2], [2, 1, 3, 0]]

# P4
P4 = [2, 4, 3, 1]


# 置换
def permute(bits, permutation):
    return [bits[i - 1] for i in permutation]


# 左移
def left_shift(bits, shifts):
    return bits[shifts:] + bits[:shifts]


# 异或
def xor(bits1, bits2):
    return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]


# 二进制（4位）转十进制
def bin2dec(binary):
    return binary[0] * 2 ** 3 + binary[1] * 2 ** 2 + binary[2] * 2 + binary[3]


# 十进制转二进制（2位）
def dec2bin(value):
    return [int(i) for i in format(value, '02b')]


# s盒
def sbox(bits, sbox):
    row = bits[0] * 2 + bits[3]
    col = bits[1] * 2 + bits[2]
    return dec2bin(sbox[row][col])


# fk函数
def fk(bits, subkey):
    left, right = bits[:4], bits[4:]
    right_expanded = permute(right, EP)
    right_subkey = xor(right_expanded, subkey)

    left_sbox = sbox(right_subkey[:4], S1)
    right_sbox = sbox(right_subkey[4:], S2)

    sbox_output = left_sbox + right_sbox
    sbox_output_permuted = permute(sbox_output, P4)

    return xor(left, sbox_output_permuted) + right


# 交换左右半
def switch(bits):
    return bits[4:] + bits[:4]


# 子密钥生成
def generate_keys(key):
    key = permute(key, P10)
    left, right = key[:5], key[5:]

    left = left_shift(left, 1)
    right = left_shift(right, 1)
    k1 = permute(left + right, P8)

    left = left_shift(left, 1)
    right = left_shift(right, 1)
    k2 = permute(left + right, P8)

    return k1, k2


# 加密函数
def encrypt(plaintext, key):
    plaintext = permute(plaintext, IP)
    k1, k2 = generate_keys(key)

    result = fk(plaintext, k1)
    result = switch(result)
    result = fk(result, k2)

    return permute(result, IP_INV)


# 解密函数
def decrypt(ciphertext, key):
    ciphertext = permute(ciphertext, IP)
    k1, k2 = generate_keys(key)

    result = fk(ciphertext, k2)
    result = switch(result)
    result = fk(result, k1)

    return permute(result, IP_INV)


# 字符串转位列表
def str2bits(s):
    return [int(b) for b in s]


# 位列表转字符串
def bits2str(bits):
    return ''.join(str(b) for b in bits)


# 判断输入类型
def determine_input_type(s):
    if s.isdigit():  # 判断是否全部为数字
        return 'digit'
    elif s.isalpha():  # 判断是否全部为英文字母
        return 'alpha'
    else:
        return 'invalid'


# 将字符转换为二进制
def char_to_binary(char):
    return format(ord(char), '08b')  # 转化为8位二进制


# 将文本转换为二进制串列表，每8位一组
def text_to_bits(text):
    bits = []
    for char in text:
        bits.extend([int(b) for b in format(ord(char), '08b')])
    return bits


# 将二进制串列表转换回文本，每8位为一组
def bits_to_text(bits):
    text = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]
        text.append(chr(int(''.join(map(str, byte)), 2)))
    return ''.join(text)


# 加密文本，处理每8位一组的分组，并保持输出为二进制形式
def encrypt_text_to_binary(bits, key):
    ciphertext_bits = []
    for i in range(0, len(bits), 8):
        block = bits[i:i + 8]
        if len(block) < 8:
            block += [0] * (8 - len(block))  # 填充0使其满足8位
        encrypted_block = encrypt(block, key)  # 加密
        ciphertext_bits.extend(encrypted_block)
    # 将加密后的二进制转换为字符串输出
    return ''.join(map(str, ciphertext_bits))  # 输出二进制字符串


# 解密二进制字符串回明文
def decrypt_binary(bits, key):
    plaintext_bits = []
    for i in range(0, len(bits), 8):
        block = bits[i:i + 8]
        if len(block) < 8:
            block += [0] * (8 - len(block))  # 填充0使其满足8位
        decrypted_block = decrypt(block, key)  # 执行解密
        plaintext_bits.extend(decrypted_block)
    return plaintext_bits


# 解密二进制字符串回明文
def decrypt_binary_to_text(bits, key):
    plaintext_bits = decrypt_binary(bits, key)
    return bits_to_text(plaintext_bits)  # 转换回明文


# 加密和解密函数
def encrypt_message():
    plaintext = entry_plaintext.get()
    key = entry_key.get()
    if len(key) == 10:  # 确保密钥长度正确
        key_bits = str2bits(key)
        input_type = determine_input_type(plaintext)
        if input_type == 'digit':
            # 检查是否为8位的倍数
            if len(plaintext) % 8 != 0:
                messagebox.showerror("Error", "输入长度必须是8位的倍数。")
                return
            plaintext_bits = str2bits(plaintext)
            ciphertext_binary = encrypt_text_to_binary(plaintext_bits, key_bits)
        elif input_type == 'alpha':
            plaintext_bits = text_to_bits(plaintext)
            ciphertext_binary = encrypt_text_to_binary(plaintext_bits, key_bits)
        else:
            messagebox.showerror("Error", "输入类型无效。")
            return
        entry_ciphertext.delete(0, tk.END)
        entry_ciphertext.insert(0, ciphertext_binary)
    else:
        messagebox.showerror("Error", "密钥长度必须为10位。")


def decrypt_to_binary():
    ciphertext_binary = entry_ciphertext.get()
    key = entry_key.get()
    if len(key) == 10:  # 确保密钥长度正确
        key_bits = str2bits(key)
        if len(ciphertext_binary) % 8 != 0:
            messagebox.showerror("Error", "输入长度必须是8位的倍数。")
            return
        ciphertext_bits = str2bits(ciphertext_binary)
        plaintext_bits = decrypt_binary(ciphertext_bits, key_bits)
        plaintext_binary_str = ''.join(map(str, plaintext_bits))
        entry_plaintext.delete(0, tk.END)
        entry_plaintext.insert(0, plaintext_binary_str)
    else:
        messagebox.showerror("Error", "密钥长度必须为10位。")


def decrypt_to_text():
    ciphertext_binary = entry_ciphertext.get()
    key = entry_key.get()
    if len(key) == 10:  # 确保密钥长度正确
        key_bits = str2bits(key)
        if len(ciphertext_binary) % 8 != 0:
            messagebox.showerror("Error", "输入长度必须是8位的倍数。")
            return
        ciphertext_bits = str2bits(ciphertext_binary)
        plaintext = decrypt_binary_to_text(ciphertext_bits, key_bits)
        entry_plaintext.delete(0, tk.END)
        entry_plaintext.insert(0, plaintext)
    else:
        messagebox.showerror("Error", "密钥长度必须为10位。")


# 暴力破解
def brute_force_gui():
    plaintext = entry_plaintext.get()
    ciphertext = entry_ciphertext.get()

    # 处理明文和密文的输入
    input_type = determine_input_type(plaintext)
    if input_type == 'digit':
        processed_plaintext = str2bits(plaintext)
    elif input_type == 'alpha':
        processed_plaintext = text_to_bits(plaintext)
    else:
        messagebox.showerror("Error", "输入类型无效。")
        return

    processed_ciphertext = str2bits(ciphertext)
    if len(processed_plaintext) % 8 != 0 or len(processed_ciphertext) % 8 != 0:
        messagebox.showerror("Error", "明文和密文必须是8位的倍数。")
        return

    start_time = time.time()  # 记录开始时间
    possible_keys = []  # 用于存储所有可能的密钥

    # 开始暴力破解，共有1024个可能的密钥
    for i in range(1024):
        key = [int(b) for b in format(i, '010b')]  # 生成10位二进制密钥
        encrypted = encrypt(processed_plaintext[:8], key)

        if encrypted == processed_ciphertext[:8]:
            possible_keys.append(bits2str(key))  # 将找到的密钥添加到列表中

    end_time = time.time()  # 记录结束时间
    elapsed_time = end_time - start_time

    if possible_keys:
        # 如果找到可能的密钥，显示所有密钥
        keys_str = " / ".join(possible_keys)
        messagebox.showinfo("暴力破解结果", f"找到的密钥: {keys_str}\n耗时: {elapsed_time:.4f}秒")
    else:
        messagebox.showinfo("暴力破解结果", f"未找到正确密钥\n耗时: {elapsed_time:.4f}秒")


# GUI
root = tk.Tk()
root.title("S-DES 加密/解密")

# 明文输入框
label_plaintext = tk.Label(root, text="明文（8n位二进制或英文字母）:")
label_plaintext.grid(row=0, column=0)
entry_plaintext = tk.Entry(root)
entry_plaintext.grid(row=0, column=1)

# 密钥输入框
label_key = tk.Label(root, text="密钥 (10位二进制):")
label_key.grid(row=1, column=0)
entry_key = tk.Entry(root)
entry_key.grid(row=1, column=1)

# 密文输入框
label_ciphertext = tk.Label(root, text="密文 (二进制):")
label_ciphertext.grid(row=2, column=0)
entry_ciphertext = tk.Entry(root)
entry_ciphertext.grid(row=2, column=1)

# 加密按钮
button_encrypt = tk.Button(root, text="加密", command=encrypt_message)
button_encrypt.grid(row=3, column=0)

# 解密为二进制按钮
button_decrypt_binary = tk.Button(root, text="解密为二进制", command=decrypt_to_binary)
button_decrypt_binary.grid(row=3, column=1)

# 解密为字母按钮
button_decrypt_text = tk.Button(root, text="解密为字母", command=decrypt_to_text)
button_decrypt_text.grid(row=3, column=2)

# 暴力破解按钮
button_bruteforce = tk.Button(root, text="暴力破解", command=brute_force_gui)
button_bruteforce.grid(row=4, column=0, columnspan=3)

root.mainloop()
