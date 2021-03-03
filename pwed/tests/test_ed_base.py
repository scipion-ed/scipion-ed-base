# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se) [1]
# *
# * [1] SciLifeLab, Stockholm University
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os

import pyworkflow as pw
import pyworkflow.tests as pwtests

import pwed
from pwed.objects import DiffractionImage, SetOfDiffractionImages
from pwed.protocols import ProtImportDiffractionImages


pw.Config.setDomain(pwed)


class TestEdBase(pwtests.BaseTest):
    @classmethod
    def setUpClass(cls):
        pwtests.setupTestOutput(cls)

    def mockHeader(self):
        header_dict = {"HEADER_BYTES": "512",
                       "DIM": "2",
                       "BYTE_ORDER": "little_endian",
                       "TYPE": "unsigned_short",
                       "SIZE1": "516",
                       "SIZE2": "516",
                       "PIXEL_SIZE": "0.055",
                       "BIN": "1x1",
                       "BIN_TYPE": "HW",
                       "ADC": "fast",
                       "CREV": "1",
                       "BEAMLINE": "TimePix_SU",
                       "DETECTOR_SN": "901",
                       "DATE": "2019-05-03 12:10:21.302198",
                       "TIME": "0.3",
                       "DISTANCE": "532.2773",
                       "TWOTHETA": "0.0",
                       "PHI": "-33.9000",
                       "OSC_START": "-33.9000",
                       "OSC_RANGE": "0.3512",
                       "WAVELENGTH": "0.0251",
                       "BEAM_CENTER_X": "219.7000",
                       "BEAM_CENTER_Y": "226.6500",
                       "DENZO_X_BEAM": "12.4657",
                       "DENZO_Y_BEAM": "12.0835",
                       }
        return header_dict

    def test_plugin(self):
        self.assertTrue(hasattr(pwed, 'Domain'))

        # Check that defined objects here are found
        objects = pwed.Domain.getObjects()

        expected = ['DiffractionImage', 'SetOfDiffractionImages']
        for e in expected:
            self.assertTrue(
                e in objects, "%s should be in Domain.getObjects" % e)

    def test_create_diffractionImages(self):
        setFn = self.getOutputPath('diffraction-images.sqlite')
        pw.utils.cleanPath(setFn)

        print("Creating set: %s" % os.path.abspath(setFn))
        testSet = SetOfDiffractionImages(filename=setFn)

        dImg = DiffractionImage()
        pattern = '/data/experiment01/images/img%04d.img'
        N = 100
        h = self.mockHeader()

        for i in range(1, N+1):
            dImg.setFileName(pattern % i)
            dImg.setObjId(i)

            dImg.setPixelSize(float(h.get('PIXEL_SIZE')))
            dImg.setDim(int(h.get('SIZE1')))
            dImg.setWavelength(float(h.get('WAVELENGTH')))
            dImg.setDistance(float(h.get('DISTANCE')))
            dImg.setOscillation(float(h.get('OSC_START')),
                                float(h.get('OSC_RANGE')))
            dImg.setBeamCenter(float(h.get('BEAM_CENTER_X')),
                               float(h.get('BEAM_CENTER_Y')))
            dImg.setExposureTime(float(h.get('TIME')))
            dImg.setTwoTheta(float(h.get('TWOTHETA')))
            testSet.append(dImg)

        testSet.write()
        testSet.close()

        testSet2 = SetOfDiffractionImages(filename=setFn)
        self.assertEqual(testSet2.getSize(), N)
        for dImg2 in testSet2:
            self.assertEqual(dImg2.getPixelSize(), 0.055)
            self.assertEqual(dImg2.getDim(), (516, 516))
            self.assertEqual(dImg2.getWavelength(), 0.0251)
            self.assertEqual(dImg2.getDistance(), 532.2773)
            self.assertEqual(dImg2.getOscillation(), (-33.9000, 0.3512))
            self.assertEqual(dImg2.getBeamCenter(), (219.7000, 226.6500))
            self.assertEqual(dImg2.getExposureTime(), 0.3)
            self.assertEqual(dImg2.getTwoTheta(), 0.0)

        testSet2.close()


class TestEdBaseProtocols(pwtests.BaseTest):
    @classmethod
    def setUpClass(cls):
        pwtests.setupTestProject(cls, writeLocalConfig=True)
        cls.dataPath = pwed.Config.SCIPION_ED_TESTDATA

        if not os.path.exists(cls.dataPath):
            raise Exception("Can not run ED tests, missing file:\n  %s"
                            % cls.dataPath)

    def _runImportImages(self, filesPattern, **kwargs):
        protImport = self.newProtocol(
            ProtImportDiffractionImages,
            filesPath=os.path.join(self.dataPath),
            filesPattern=filesPattern,
            **kwargs)
        self.launchProtocol(protImport)
        return protImport

    def mockOverwrite(self):
        owDict = {}
        owDict["overwriteWavelength"] = "1000"
        owDict["overwriteSize1"] = "1000"
        owDict["overwriteSize2"] = "1000"
        owDict["overwritePixelSize"] = "1000"
        owDict["overwriteExposureTime"] = "1000"
        owDict["overwriteDetectorDistance"] = "1000"
        owDict["overwriteOscStart"] = "1000"
        owDict["overwriteOscRange"] = "1000"
        owDict["overwriteBeamCenterX"] = "1000"
        owDict["overwriteBeamCenterY"] = "1000"
        return owDict

    def test_import(self):

        protImport = self._runImportImages(
            'lysozyme/experiment_14/SMV/data/{TI}.img')
        output = getattr(protImport, 'outputDiffractionImages', None)
        self.assertFalse(output is None)
        for img in output:
            self.assertFalse(img.getFileName() is None)
            self.assertFalse(img.getObjId() is None)
            self.assertFalse(img.getPixelSize() is None)
            self.assertFalse(img.getDim() is None)
            self.assertFalse(img.getWavelength() is None)
            self.assertFalse(img.getDistance() is None)
            self.assertFalse(img.getOscillation() is None)
            self.assertFalse(img.getBeamCenter() is None)
            self.assertFalse(img.getExposureTime() is None)
            self.assertFalse(img.getTwoTheta() is None)

        overwriteDict = self.mockOverwrite()
        owImport = self._runImportImages(
            'lysozyme/experiment_14/SMV/data/{TI}.img', **overwriteDict)
        output = getattr(owImport, 'outputDiffractionImages', None)
        self.assertFalse(output is None)
        for img in output:
            self.assertEqual(img.getPixelSize(), 1000)
            self.assertEqual(img.getDim(), (1000, 1000))
            self.assertEqual(img.getWavelength(), 1000)
            self.assertEqual(img.getDistance(), 1000)
            self.assertEqual(img.getOscillation(), (1000, 1000))
            self.assertEqual(img.getBeamCenter(), (1000, 1000))
            self.assertEqual(img.getExposureTime(), 1000)

        protImport2 = self._runImportImages(
            'lysozyme/experiment_14/SMV/data/{TI}.img', skipImages=10, rotationAxis='1000,1000,0')
        output = getattr(protImport2, 'outputDiffractionImages', None)
        self.assertFalse(output is None)
        for img in output:
            self.assertNotEqual(img.getObjId(), 0)
            if img.getObjId() % 10 == 0:
                self.assertTrue(img.getIgnore())
            self.assertEqual(img.getRotationAxis(), (1000.0, 1000.0, 0.0))
