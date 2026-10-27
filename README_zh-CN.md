# QuantifiableCracks — 第一期

**版本：v0.1.0；发布批次：Phase 1 / 第一期。**

QuantifiableCracks面向结构表面裂纹分割研究。本批数据是第一期，后续将持续补充，新增数据与修订内容会通过新版本和更新日志说明。每个版本的实际内容以样本清单为准。

## 本期内容

| 内容 | 数量 | 格式与含义 |
|---|---:|---|
| 裂纹图像 | 158 | 512×512像素、RGB PNG，处理后的ROI裁剪图 |
| 二值掩膜 | 158 | 512×512像素、灰度PNG，背景0、裂纹255 |
| JSON标注 | 158 | 从PNG掩膜导出的多边形与精确RLE编码 |

共158组配对样本、474个数据文件。ROI图像在两个来源目录中的重复副本已合并，PNG图像与掩膜的文件字节保持不变。

## 目录与配对

```text
data/phase1/images/<id>.png
data/phase1/masks/<id>mask.png
data/phase1/annotations/<id>mask.json
metadata/manifest.csv
metadata/annotation_fidelity.csv
metadata/release_metadata.json
tools/validate_dataset.py
```

`<id>`为保留的原始样本文件名标识。每组图像、掩膜和JSON通过同一标识配对。文件名前缀尚未提供经确认的试件映射，不能仅凭名称推断独立试件或分组划分。

JSON的`imagePath`与`sourceMask`已分别改成相对于JSON目录的`../images/<id>.png`和`../masks/<id>mask.png`。仅规范了这两个路径字段和JSON文本排版；多边形坐标、RLE计数及其他标注值未改动。

## 掩膜与多边形的使用

PNG与JSON中的自定义`mask_rle`均可提供精确像素掩膜，158组RLE解码结果全部与PNG一致。JSON采用Labelme风格多边形结构，并附加未压缩COCO风格RLE；它不是完整的COCO数据集格式。

多边形适合查看和编辑，重新栅格化时可能填充内部孔洞或改变边界。107组多边形重建与PNG完全一致，51组存在差异。**像素级评估和几何测量应使用PNG掩膜或精确RLE。**详细字段与解码示例见[标注格式说明](docs/ANNOTATION_FORMAT.md)。

## 校验与读取

Python环境需安装NumPy和Pillow：

```bash
python -m pip install -r requirements.txt
python tools/validate_dataset.py
```

脚本会检查样本配对、文件完整性、尺寸、掩膜值、相对路径、RLE一致性和SHA-256校验值。完整文件哈希见`checksums.sha256`；单样本路径及哈希见`metadata/manifest.csv`。图像读取示例见[英文README](README.md)。

## 本批范围与后续更新

本批提供处理后的ROI、掩膜和JSON；尚未附带原始全幅照片、相机内参、ArUco角点、逐图物理尺度元数据、正式训练/验证/测试划分或几何测量结果。512×512像素尺寸本身不能确定毫米尺度。进行物理量复现或试件分组评估时，需要对应的标定或分组信息。

后续将持续扩充数据。已有样本标识保持稳定，新增样本使用新标识；标注修订、元数据补充或文件撤回均在新版本与`CHANGELOG.md`中记录。已公开的版本快照应保持不变。引用数据时请记录批次、版本标签或确切提交号；本版本尚未分配DOI。

## 许可与相关工具

本数据集采用**MIT许可**，见[LICENSE](LICENSE)。

相关工具：[Semi-auto-Annotating-tool](https://github.com/levyw3847-arch/Semi-auto-Annotating-tool)。

数据仓库地址：[QuantifiableCracks](https://github.com/levyw3847-arch/QuantifiableCracks)。
