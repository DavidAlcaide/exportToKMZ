import os
from lxml import etree
import kml_cdata as KML
import progressbar
from zipfile import ZipFile


if __name__ == '__main__':

    _projectName = "GIS Zona 1"
    nameSpaces = {'df': 'http://www.opengis.net/kml/2.2', 'gx': 'http://www.google.com/kml/ext/2.2', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance' }
    _project_styles = []

    _layers = list(filter(lambda x: '.shp' in x, os.listdir('./data')))
    f = open('./models/kml_model.kml')
    _kml = etree.parse(f)

    _kml_document = _kml.getroot().find('./')
    bar = progressbar.ProgressBar(0, 100)

    for k, _layer in enumerate(_layers):
        KML.createKMLLayer(_kml_document, f'./data/{_layer}', _project_styles)
        bar.update(100/len(_layers)*k)

    _kml.getroot().find('./').extend(_project_styles)

    # Cerramos y salvamos el archivo creado
    f.close()

    for nameSpace in nameSpaces.keys():
        etree.register_namespace(nameSpace, nameSpaces[nameSpace])

    _kml.write(f'./generated/{_projectName}.kml', xml_declaration=True, pretty_print=True, encoding="utf-8")


    # Generaxión del kmz

    with ZipFile(f'./generated/{_projectName}.kmz', 'w') as kmz:
        kmz.write(f'./generated/{_projectName}.kml', f'./{_projectName}.kml')
        for icon in os.listdir('./data/styles'):
            kmz.write(f'./data/styles/{icon}', f'./{icon}')




