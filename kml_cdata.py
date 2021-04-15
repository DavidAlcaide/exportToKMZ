from lxml import etree
from shapely.geometry import Point, LineString
import geopandas as gp
import pyproj as prj
from typing import List


def makeDescription(pointData: gp.geoseries) -> etree.Element:
    """
    :param pointData:
    :return:
    """
    _description = etree.Element('description')

    description_content = f'<table class="esri-widget__table"><tbody>'

    for k in pointData.keys()[:-3]:
        description_content += f'<tr><th class="esri-feature__field-header">{k}</th><td>{pointData.loc[k]}</td></tr>'

    description_content += '</tbody></table>'

    _description.text = etree.CDATA(description_content)

    return _description


def makeIconStyle(iconId: str) -> etree.Element:
    """
    :param iconId:
    :return:
    """

    _iconStyle = etree.Element('IconStyle')
    _scale = etree.Element('scale')
    _scale.text = '1.5'
    _icon = etree.Element('Icon')
    _href = etree.Element('href')
    _href.text = f'{iconId}.png'
    _icon.append(_href)
    _iconStyle.extend([_scale, _icon])

    return _iconStyle


def makePointStyle(stylesId: List[str]) -> List[etree.Element]:
    """
    :param stylesId:
    :return:
    """
    styles = []
    for style in stylesId:
        _style = etree.Element('Style', {'id': f'{style}'})
        _iconStyle = makeIconStyle(style)
        _style.append(_iconStyle)

        styles.append(_style)

    return styles


def transformCoordinates(xcoord: float, ycoord: float) -> List[str]:
    """
    :param xcoord:
    :param ycoord:
    :return:
    """
    _transform = prj.Transformer.from_crs('EPSG:25830', 'EPSG:4326', always_xy=True)
    return list(map(lambda x: str(x), list(_transform.transform(xcoord, ycoord))))


def makeExtendedData(pointData: gp.geoseries):
    """
    :param pointData:
    :return:
    """
    _extendedData = etree.Element('ExtendedData')

    for i in range(pointData.shape[0] - 3):  #Eliminamos los campos Style, Label, y geometry
        _data = etree.Element('Data', {'name': f'{pointData.keys()[i]}'})
        _value = etree.Element('value')
        _value.text = str(pointData[pointData.keys()[i]])
        _data.append(_value)
        _extendedData.append(_data)

    return _extendedData


def makePoint(point: Point) -> etree.Element:
    """
    :param point:
    :return:
    """

    _point = etree.Element('Point')
    _altitude = etree.Element('altitudeMode')
    _altitude.text = 'clampToGround'
    _coordinates = etree.Element('coordinates')
    _coordinates.text = f'{point.x}, {point.y}, 0'
    _point.extend([_altitude, _coordinates])

    return _point


def createPointPlaceMark(pointData: gp.geoseries, index: int) -> etree.Element:
    """
    :param index:
    :param pointData:
    :return:
    """

    _placeMark = etree.Element('Placemark', {'id': str(index)})
    _name = etree.SubElement(_placeMark, 'name')
    _name.text = pointData['Label']
    _placeMark.append(makeExtendedData(pointData))
    _placeMark.append(makePoint(pointData['geometry']))
    _styleUrl = etree.Element('styleUrl')
    _styleUrl.text = f'#{pointData["Style"]}'
    _placeMark.append(_styleUrl)
    _placeMark.append(makeDescription(pointData))

    return _placeMark


def addPointKMLLayer(_kml_document: etree.Element, shpData: gp.GeoDataFrame, layerName: str, project_styles: List[etree.Element]) -> None:
    """
    :param _kml_document:
    :param project_styles:
    :param shpData:
    :param layerName:
    :return:
    """
    _folder = etree.SubElement(_kml_document, 'Folder', {'id': layerName})
    _name = etree.Element('text')
    _name.text = layerName
    _folder.append(_name)
    _folder.append(etree.Element('Snippet'))

    for i in range(shpData.shape[0]):
        _placemark = createPointPlaceMark(shpData.loc[i], i)
        _folder.append(_placemark)

    _styles = makePointStyle(list(set(shpData.loc[:, 'Style'])))
    project_styles.extend(_styles)



def createKMLLayer(_kml_document: etree.Element, path: str, project_styles: List[etree.Element]) -> None:
    """
    :param _kml_document:
    :param path:
    :return:
    """

    shpData = gp.read_file(path)

    shpData = shpData[shpData['geometry'] != None]
    shpData.reset_index(inplace=True)

    shpData.to_crs(4326, inplace=True)

    if isinstance(shpData.geometry[0], Point):
        addPointKMLLayer(_kml_document, shpData, path.split('/')[-1].split('.shp')[0], project_styles)
    elif isinstance(shpData.geometry[0], LineString):
        #addLineKMLLayer(_kml_document, shpData,  path.split('/')[-1].split('.shp')[0])
        pass
    else:
        print('Capa no soportada por el sistema')