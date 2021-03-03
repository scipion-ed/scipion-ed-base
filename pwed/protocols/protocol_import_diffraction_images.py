# **************************************************************************
# *
# * Authors:     J.M. De la Rosa Trevin (delarosatrevin@scilifelab.se) [1]
# *              V. E.G. Bengtsson (viktor.bengtsson@mmk.su.se) [2]
# *
# * [1] SciLifeLab, Stockholm University
# * [2] Department of Materials and Environmental Chemistry, Stockholm University
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
import re
import pathlib
import string
from glob import glob

import pyworkflow as pw
import pyworkflow.protocol as pwprot

from pwed.objects import DiffractionImage, SetOfDiffractionImages
from .protocol_base import EdBaseProtocol


class ProtImportDiffractionImages(EdBaseProtocol):
    """ Base class for other Import protocols.
    All imports protocols will have:
    1) Several options to import from (_getImportOptions function)
    2) First option will always be "from files". (for this option
      files with a given pattern will be retrieved  and the ### will
      be used to mark an ID part from the filename.
      - For each file a function to process it will be called
        (_importFile(fileName, fileId))
    """
    IMPORT_FROM_FILES = 0

    # How to handle the input files into the project
    IMPORT_COPY_FILES = 0
    IMPORT_LINK_ABS = 1
    IMPORT_LINK_REL = 2

    IMPORT_TYPE_MICS = 0
    IMPORT_TYPE_MOVS = 1

    ANGLES_FROM_FILES = 0
    ANGLES_FROM_HEADER = 1
    ANGLES_FROM_MDOC = 2

    _label = 'import diffraction images'

    # -------------------------- DEFINE param functions -----------------------
    def _defineParams(self, form):
        form.addSection(label='Import')

        form.addParam('filesPath', pwprot.PathParam,
                      label="Files directory",
                      help="Directory with images to be imported.")
        form.addParam('filesPattern', pwprot.StringParam,
                      label='Pattern',
                      help="Pattern of the experiment\n\n"
                           "The pattern can contain standard wildcards such as\n"
                           "*, ?, etc.\n\n"
                           "It should also contains the following special tag:"
                           "   {TI}: image identifier "
                           "         (an integer value, unique within the experiment).\n"
                           "Examples:\n"
                           "")
        form.addParam('importAction', pwprot.EnumParam,
                      default=self.IMPORT_LINK_REL,
                      choices=['Copy files',
                               'Absolute symlink',
                               'Relative symlink'],
                      display=pwprot.EnumParam.DISPLAY_HLIST,
                      expertLevel=pwprot.LEVEL_ADVANCED,
                      label="Import action on files",
                      help="By default ...")

        form.addParam('skipImages', pwprot.IntParam, default=None,
                      allowsNull=True,
                      label="Skip images",
                      help="Images to skip during processing.\n"
                           "Required for data collected with defocusing to "
                           "track images back to the aperture or beam.\n"
                           "A value of 10 will skip every 10th frame.")

        form.addParam('replaceRotationAxis', pwprot.BooleanParam,
                      label='Overwrite rotation axis?', default=False,
                      help="The rotation axis is an instrument parameter. If the correct parameter is not given automatically, it might need to be overwritten here.",
                      expertLevel=pwprot.LEVEL_ADVANCED,
                      )

        form.addParam('rotationAxis', pwprot.StringParam, default=None,
                      allowsNull=True,
                      label="Rotation axis",
                      help="The goniometer rotation axis relative to the image.",
                      condition="replaceRotationAxis",
                      )

        # Enable using template
        group = form.group = form.addGroup('Template input')
        group.addParam('useTemplate', pwprot.BooleanParam,
                       label='Use template syntax', default=False,
                       help="Explicitly set a template syntax to use for DIALS import or XDS input file",
                       )
        group.addParam('tsReplacement', pwprot.StringParam,
                       label='String to insert instead of {TI}',
                       default='00###',
                       help="Only useful in XDS or when using template in DIALS.",
                       )

        group = form.addGroup('Corrected parameters')

        group.addParam('overwriteWavelength', pwprot.StringParam,
                       default=None,
                       allowsNull=True,
                       label="Corrected wavelength",
                       help="Use this value instead of the value found in the file header.")

        group.addParam('overwriteDetectorDistance', pwprot.StringParam,
                       default=None,
                       allowsNull=True,
                       label="Set detector distance",
                       help="Use a different detector distance than found in the file header.")

        group = form.addGroup('Overwrite file header',
                              expertLevel=pwprot.LEVEL_ADVANCED,)

        group.addParam('overwriteSize1', pwprot.StringParam,
                       default=None,
                       allowsNull=True,
                       label="Set Size1",
                       help="Overwrites the Size1 found from the headerfile.")

        group.addParam('overwriteSize2', pwprot.StringParam,
                       default=None,
                       allowsNull=True,
                       label="Set Size2",
                       help="Overwrites the Size2 found from the headerfile.")

        group.addParam('overwritePixelSize', pwprot.StringParam,
                       default=None,
                       allowsNull=True,
                       label="Set pixel size",
                       help="Overwrites the pixel size found from the headerfile.")

        group.addParam('overwriteExposureTime', pwprot.StringParam,
                       default=None,
                       allowsNull=True,
                       label="Set exposure time",
                       help="Overwrites the exposure time found from the headerfile.")

        group.addParam('overwriteOscStart', pwprot.StringParam,
                       default=None,
                       allowsNull=True,
                       label="Set starting angle",
                       help="Overwrites the starting angle found from the headerfile.")

        group.addParam('overwriteOscRange', pwprot.StringParam,
                       default=None,
                       allowsNull=True,
                       label="Set oscillation range",
                       help="Overwrites the oscillation range found from the headerfile.")

        group.addParam('overwriteBeamCenterX', pwprot.StringParam,
                       default=None,
                       allowsNull=True,
                       label="Set beam center X",
                       help="Overwrites the beam center X found from the headerfile.")

        group.addParam('overwriteBeamCenterY', pwprot.StringParam,
                       default=None,
                       allowsNull=True,
                       label="Set beam center Y",
                       help="Overwrites the beam center Y found from the headerfile.")

    # -------------------------- INSERT functions ------------------------------
    def _insertAllSteps(self):
        self.loadPatterns()
        self._insertFunctionStep('convertInputStep', self._pattern)
        self._insertFunctionStep('createOutputStep')

    # -------------------------- STEPS functions -------------------------------
    def convertInputStep(self, pattern):
        self.loadPatterns()
        self.info("Using glob pattern: '%s'" % self._globPattern)
        self.info("Using regex pattern: '%s'" % self._regexPattern)

    def createOutputStep(self, **kwargs):
        outputSet = self._createSetOfDiffractionImages()
        outputSet.setDialsModel(kwargs.get('dialsModel'))
        outputSet.setSkipImages(self.skipImages.get())

        dImg = DiffractionImage()

        for f, ti in self.getMatchingFiles():
            dImg.setFileName(f)
            dImg.setObjId(int(ti))
            if self.skipImages.get() is not None:
                dImg.setIgnore(true_or_false=bool(int(ti) %
                                                  self.skipImages.get() == 0))
            if self.getRotationAxis():
                dImg.setRotationAxis(self.getRotationAxis())

            try:
                if f.endswith('.img'):
                    h = self.readSmvHeader(f)
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
            except Exception as e:
                print(e)

            outputSet.append(dImg)

        outputSet.write()

        self._defineOutputs(outputDiffractionImages=outputSet)

    # -------------------------- INFO functions -------------------------------
    def _validate(self):
        self.loadPatterns()
        errors = []
        if len(glob(self._globPattern)) < 1:
            errors.append(
                "No files found. This might be due to an empty directory or using the wrong file format")
        if self.useTemplate and self.badTsReplacement():
            errors.append("Only use digits and # to replace {TI}.")
        return errors

    def _summary(self):
        summary = []
        summary.append('Data in {}'.format(
            self.getFileParents(self.getMatchingFiles())))

        return summary

    # -------------------------- BASE methods to be overridden -----------------
    def _getImportChoices(self):
        """ Return a list of possible choices
        from which the import can be done.
        (usually packages form such as: xmipp3, eman2, relion...etc.
        """
        return ['files']

    # -------------------------- UTILS functions ------------------------------
    def loadPatterns(self):
        """ Expand the pattern using environ vars or username
        and also replacing special character # by digit matching.
        """
        self._pattern = self.combinePaths(
            self.getFilesDir(), self.getFilesPattern())

        def _replace(p, ti):
            p = p.replace('{TI}', ti)
            return p

        self._regexPattern = _replace(self._pattern.replace('*', '(.*)'),
                                      r'(?P<TI>\d+)')
        self._regex = re.compile(self._regexPattern)
        self._globPattern = _replace(self._pattern, '*')
        self._templatePattern = _replace(
            self._pattern, self.tsReplacement.get())

    def combinePaths(self, p1, p2):
        # Remove file name from end of p1
        if p1.split('.')[-1] == p2.split('.')[-1]:
            p1 = "/".join(p1.split('/')[0:-1])
        # Combine p1 and p2, but ignore overlapping directory names
        path = os.path.join(
            p1, *[i for i in p2.split('/') if i not in p1.split('/')])
        return path

    def badTsReplacement(self):
        return bool(re.compile(r'[^0-9#]').search(self.tsReplacement.get()))

    def getFilesDir(self):
        return self.filesPath.get('').strip()

    def getFilesPattern(self):
        return self.filesPattern.get('').strip()

    def getMatchingFiles(self):
        """ Return a sorted list with the paths of files that
        matched the pattern.
        """
        self.loadPatterns()

        filePaths = glob(self._globPattern)
        filePaths.sort()

        matchingFiles = []
        for f in filePaths:
            m = self._regex.match(f)
            if m is not None:
                matchingFiles.append((f, int(m.group('TI'))))

        return matchingFiles

    def getRotationAxis(self):
        try:
            axis = [float(s)
                    for s in re.split('[,\s]', self.rotationAxis.get()) if s]
        except Exception as e:
            self.debug("Failed getting rotation axis due to exception:\n"
                       "{}".format(e))
            axis = None
        return axis

    def getFileParents(self, file_list):
        uniquePaths = []
        for f in file_list:
            p = str(pathlib.Path(f[0]).parent)
            if p not in uniquePaths:
                uniquePaths.append(p)
        if len(uniquePaths) == 1:
            return uniquePaths[0]
        else:
            return uniquePaths

    def getCopyOrLink(self):
        # Set a function to copyFile or createLink
        # depending in the user selected option
        if self.copyFiles:
            return pw.utils.copyFile
        else:
            return pw.utils.createAbsLink

    def readSmvHeader(self, image_file):
        # Reimplemented from get_smv_header in
        # https://github.com/dials/dxtbx/blob/master/format/FormatSMV.py
        with open(image_file, "rb") as fh:
            header_info = fh.read(45).decode("ascii", "ignore")
            header_size = int(
                header_info.split("\n")[1].split(
                    "=")[1].replace(";", "").strip()
            )
            header_text = fh.read(header_size).decode("ascii", "ignore")
        header_dictionary = {}

        # Check that we have the whole header, contained within { }.  Stop
        # extracting data once a record solely composed of a closing curly
        # brace is seen.  If there is no such character in header_text
        # either HEADER_BYTES caused a short read of the header or the
        # header is malformed.

        overwrites = self._overwriteParams()

        for record in header_text.split("\n"):
            if record == "}":
                break
            if "=" not in record:
                continue

            key, value = record.replace(";", "").split("=")

            header_dictionary[key.strip()] = value.strip()
            header_dictionary.update(overwrites)

        return header_dictionary

    def _overwriteParams(self):
        new_params = {}
        if self.overwriteSize1.get():
            new_params['SIZE1'] = self.overwriteSize1.get()

        if self.overwriteSize2.get():
            new_params['SIZE2'] = self.overwriteSize2.get()

        if self.overwritePixelSize.get():
            new_params['PIXEL_SIZE'] = self.overwritePixelSize.get()

        if self.overwriteExposureTime.get():
            new_params['TIME'] = self.overwriteExposureTime.get()

        if self.overwriteDetectorDistance.get():
            new_params['DISTANCE'] = self.overwriteDetectorDistance.get()

        if self.overwriteOscStart.get():
            new_params['OSC_START'] = self.overwriteOscStart.get()

        if self.overwriteOscRange.get():
            new_params['OSC_RANGE'] = self.overwriteOscRange.get()

        if self.overwriteWavelength.get():
            new_params['WAVELENGTH'] = self.overwriteWavelength.get()

        if self.overwriteBeamCenterX.get():
            new_params['BEAM_CENTER_X'] = self.overwriteBeamCenterX.get()

        if self.overwriteBeamCenterY.get():
            new_params['BEAM_CENTER_Y'] = self.overwriteBeamCenterY.get()

        return new_params
