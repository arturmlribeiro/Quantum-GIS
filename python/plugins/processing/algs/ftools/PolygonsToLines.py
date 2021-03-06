# -*- coding: utf-8 -*-

"""
***************************************************************************
    PolygonsToLines.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'


from PyQt4.QtCore import *

from qgis.core import *

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.QGisLayers import QGisLayers

from processing.parameters.ParameterVector import ParameterVector

from processing.outputs.OutputVector import OutputVector

class PolygonsToLines(GeoAlgorithm):

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

    #===========================================================================
    # def getIcon(self):
    #    return QtGui.QIcon(os.path.dirname(__file__) + "/icons/to_lines.png")
    #===========================================================================

    def defineCharacteristics(self):
        self.name = "Polygons to lines"
        self.group = "Vector geometry tools"

        self.addParameter(ParameterVector(self.INPUT, "Input layer", [ParameterVector.VECTOR_TYPE_POLYGON]))

        self.addOutput(OutputVector(self.OUTPUT, "Output layer"))

    def processAlgorithm(self, progress):
        layer = QGisLayers.getObjectFromUri(self.getParameterValue(self.INPUT))

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(layer.pendingFields().toList(),
                     QGis.WKBLineString, layer.crs())

        outFeat = QgsFeature()
        inGeom = QgsGeometry()
        outGeom = QgsGeometry()

        current = 0
        features = QGisLayers.features(layer)
        total = 100.0 / float(len(features))
        for f in features:
            inGeom = f.geometry()
            attrs = f.attributes()
            lineList = self.extractAsLine(inGeom)
            outFeat.setAttributes(attrs)
            for h in lineList:
                outFeat.setGeometry(outGeom.fromPolyline(h))
                writer.addFeature(outFeat)

            current += 1
            progress.setPercentage(int(current * total))

        del writer

    def extractAsLine(self, geom):
        multiGeom = QgsGeometry()
        lines = []
        if geom.type() == QGis.Polygon:
          if geom.isMultipart():
              multiGeom = geom.asMultiPolygon()
              for i in multiGeom:
                  lines.extend(i)
          else:
              multiGeom = geom.asPolygon()
              lines = multiGeom
          return lines
        else:
            return []
