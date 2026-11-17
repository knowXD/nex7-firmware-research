# NEX-7 内核分析（vmlinux.bin）

## 基本信息

- Linux 2.6.29.6-rt24-alp_nl
- 编译器：gcc 4.3.3 (Sony CE Linux 6.0.0.4)
- 配置：SMP PREEMPT RT ARMv6
- 三个固件版本的内核代码几乎相同（1.01 vs 1.03 仅 49 字节差异，全是编译主机/时间字符串）

## 符号表已恢复

用 vmlinux-to-elf 的 kallsyms_finder 从原始内核中提取：

- 输出：nex7/kallsyms.txt（约 408KB）
- 基址：_stext = 0xC0018000，_text = 0xC0031000，_etext = 0xC01BA000
- 文件偏移 = 虚拟地址 - 0xC0018000

关键符号：

| 符号 | 地址 | 文件偏移 |
|---|---|---|
| lz77_inflate | 0xC011E450 | 0x106450 |
| lz77_deflate | 0xC011E670 | 0x106670 |
| cramfs_uncompress_block_lz77 | 0xC00ED710 | 0xD5710 |
| cmpr_load_file | 0xC0042C28 | 0x2AC28 |
| cmpr_deflate | 0xC0042A84 | 0x2AA84 |
| wbi_tsk_cmpr | 0xC00407F0 | 0x287F0 |

## lz77_inflate 反汇编要点

- 签名：lz77_inflate(in, in_len, out_len, out)
- 首字节：0x0F = 存储块，0xF0 = 压缩块
- 输出长度由调用方显式传入，函数本身不写死 4KB

## 4KB 从哪来

- cramfs 的块大小就是 4096（页大小），cramfs_uncompress_block_lz77
  是薄封装，直接以 4KB 为单位调用 lz77_inflate；
- TPZL 加载路径（cmpr_load_file）中也出现 0x1000 的边界判断；
- 这与我们从原厂镜像观测到的"每个 64KB 块 = 16 × 4096"完全吻合。

## 结论

内核里的 LZ77 编解码器与 TPZL 的 4KB 分段规则在代码层面得到确认。
以后分析任何 Sony 分区镜像，都可以用 kallsyms + r2 定位具体函数。
