# - `numpy`：做数组运算
# - `gdal`：读写遥感栅格
# - `GetDriverByName('GTiff')`：拿到写 GeoTIFF 的驱动
import numpy as np
from numpy import nan_to_num, subtract, add, divide, multiply
from osgeo import gdal, gdalconst
from osgeo.gdal import GetDriverByName

# 接收：
# - 近红外波段
# - 红光/颜色波段
# - 行数
# - 列数
# - 地理信息
# - 输出文件名
# - 输出类型
def ndvi(in_nir_band, in_colour_band, in_rows, in_cols, in_geotransform, out_tiff, data_type=gdal.GDT_Float32):

    """
    Performs an NDVI calculation given two input bands, as well as other information that can be retrieved from the
    original image.
    @param in_nir_band A GDAL band object representing the near-infrared image data.
    @type in_nir_band GDALRasterBand
    @param in_colour_band A GDAL band object representing the colour image data.
    @type: in_colour_band GDALRasterBand
    @param in_rows The number of rows in both input bands.
    @type: in_rows int
    @param in_cols The number of columns in both input bands.
    @type: in_cols int
    @param in_geotransform The geographic transformation to be applied to the output image.
    @type in_geotransform Tuple (as returned by GetGeoTransform())
    @param out_tiff Path to the desired output .tif file.
    @type: out_tiff String (should end in ".tif")
    @param data_type Data type of output image.  Valid values are gdal.UInt16 and gdal.Float32.  Default is
                      gdal.Float32
    @type data_type GDALDataType
    @return None
    """

    # Read the input bands as numpy arrays.读取波段数据到数组numpy。
    #意思是：
    # - 把 GDAL 波段读成 NumPy 数组
    # - 后面就能直接做数学运算
    # 你可以把它想成：
    # - 把遥感图片变成一个二维数值矩阵。
    np_nir = in_nir_band.ReadAsArray(0, 0, in_cols, in_rows)
    np_colour = in_colour_band.ReadAsArray(0, 0, in_cols, in_rows)

    # Convert the np arrays to 32-bit floating point to make sure division will occur properly.转成 float32
    # 如果不转成 float32，默认是 int16，除法会出问题，因为整数除法会向下取整，导致结果不正确。
    np_nir_as32 = np_nir.astype(np.float32)
    np_colour_as32 = np_colour.astype(np.float32)

    # Calculate the NDVI formula. 计算 NDVI
    # NDVI = (NIR - Red) / (NIR + Red)
    # - 分子：近红外 - 红光
    # - 分母：近红外 + 红光
    # - 最后除一下～
    numerator = subtract(np_nir_as32, np_colour_as32)
    denominator = add(np_nir_as32, np_colour_as32)
    result = divide(numerator, denominator)

    # Remove any out-of-bounds areas 处理无效值
    # - NDVI 的值域是 [-1, 1]，所以任何小于 -1 或大于 1 的值都是无效的。
    # 意思是：
    # - 把某些异常值标成 `99`
    # - 作为 NoData 的标记
    # 这类值通常表示：
    # - 没有数据
    # - 背景区域
    # - 不合法计算结果
    result[result == -0] = -99

    # Initialize a geotiff driver. 创建 GeoTIFF 输出，告诉 GDAL：我要写一个 GeoTIFF 文件。
    geotiff = GetDriverByName('GTiff')

    # If the desired output is an int16, map the domain [-1,1] to [0,255], create an int16 geotiff with one band and 如果所需输出为 int16 类型，则将域 [-1,1] 映射到 [0,255]，创建一个包含一个波段的 int16 类型 GeoTIFF 文件，并且
    # write the contents of the int16 NDVI calculation to it.  Otherwise, create a float32 geotiff with one band and 将 int16 NDVI 计算结果写入该对象。否则，创建一个包含一个波段的 float32 geotiff 对象。
    # write the contents of the float32 NDVI calculation to it. 将 float32 NDVI 计算结果的内容写入其中。
    if data_type == gdal.GDT_UInt16:
        ndvi_int8 = multiply((result + 1), (2**7 - 1))
        output = geotiff.Create(out_tiff, in_cols, in_rows, 1, gdal.GDT_Byte)
        output_band = output.GetRasterBand(1)
        output_band.SetNoDataValue(-99)
        output_band.WriteArray(ndvi_int8)
    elif data_type == gdal.GDT_Float32:
        output = geotiff.Create(out_tiff, in_cols, in_rows, 1, gdal.GDT_Float32)
        output_band = output.GetRasterBand(1)
        output_band.SetNoDataValue(-99)
        output_band.WriteArray(result)
    else:
        raise ValueError('Invalid output data type.  Valid types are gdal.UInt16 or gdal.Float32.')

    # Set the geographic transformation as the input.写入地理信息 意思是让输出结果保留原来的地理位置。
    output.SetGeoTransform(in_geotransform)

    return None

