from osgeo import gdal
from osgeo.gdal import Open
# 导入 GDAL
#单独把 Open 函数拿出来，方便直接用
from ndvi import ndvi #从 ndvi.py 里导入 ndvi() 这个函数

# Open NIR image and get its only band.打开近红外影像（NIR_IMAGE.tif）取第一波段
nir_tiff = Open(r'NIR_IMAGE.tif')
nir_band = nir_tiff.GetRasterBand(1)

# Open red image and get its only band.打开红光影像（RED_IMAGE.tif）取它的第一波段
red_tiff = Open(r'RED_IMAGE.tif')
red_band = red_tiff.GetRasterBand(1)

# Get the rows and cols from one of the images (both should always be the same)
# 从其中一张图片中获取行数和列数（两者应该始终相同）
# - `RasterYSize`：行数
# - `RasterXSize`：列数
# - `GetGeoTransform()`：拿地理参考信息，`geotransform` 很重要，因为它告诉输出影像：- 在哪儿- 怎么定位到地图上
rows, cols, geotransform = nir_tiff.RasterYSize, nir_tiff.RasterXSize, nir_tiff.GetGeoTransform()
print(geotransform)

# Set an output for a 16-bit unsigned integer (0-255)设置一个 16 位无符号整数的输出；设置输出文件名。
out_tiff_int16 = r'NDVI_INT16.tif'

# Set the output for a 32-bit floating point (-1 to 1)置一个 32 位无符号整数的输出；设置输出文件名。
out_tiff_float32 = r'NDVI_FLOAT32.tif'

# Run the function for unsigned 16-bit integer 调用核心函数，输出一个整型版本的 NDVI。
ndvi(nir_band, red_band, rows, cols, geotransform, out_tiff_int16, gdal.GDT_UInt16)

# Run the function for 32-bit floating point 调用核心函数，输出一个浮点型版本的 NDVI。
ndvi(nir_band, red_band, rows, cols, geotransform, out_tiff_float32, gdal.GDT_Float32)

print('done')
# `ndvi_demo.py` 总结
# ndvidemo.py 做的事就是：
# 1. 打开输入影像
# 2. 取波段
# 3. 取尺寸和地理信息
# 4. 调用 `ndvi()`
# 5. 输出结果
# 它是“**怎么用这个函数**”的例子。