#!/usr/bin/env python
"""
Package for storage and manipulation of seismic earth models.
"""
import itertools


class VelocityModel(object):
    def __init__(self, modelName="unknown", radiusOfEarth=6371.0,
                 mohoDepth=35.0, cmbDepth=2889.0, iocbDepth=5153.9,
                 minRadius=0.0, maxRadius=6371.0, isSpherical=True,
                 layers=None):
        """
        :type modelName: str
        :param modelName: name of the velocity model.
        :type radiusOfEarth: float
        :param radiusOfEarth: reference radius (km), usually radius of the
            earth.
        :type mohoDepth: float
        :param mohoDepth: Depth (km) of the moho. It can be input from velocity
            model (*.nd) or should be explicitly set. By default it is 35
            kilometers (from Iasp91).  For phase naming, the tau model will
            choose the closest 1st order discontinuity. Thus for most simple
            earth models these values are satisfactory. Take proper care if
            your model has a thicker crust and a discontinuity near 35 km
            depth.
        :type cmbDepth: float
        :param cmbDepth: Depth (km) of the cmb (core mantle boundary). It can
            be input from velocity model (*.nd) or should be explicitly set. By
            default it is 2889 kilometers (from Iasp91). For phase naming, the
            tau model will choose the closest 1st order discontinuity. Thus for
            most simple earth models these values are satisfactory.
        :type iocbDepth: float
        :param iocbDepth: Depth (km) of the iocb (inner core outer core
            boundary). It can be input from velocity model (*.nd) or should be
            explicitly set. By default it is 5153.9 kilometers (from Iasp91).
            For phase naming, the tau model will choose the closest 1st order
            discontinuity. Thus for most simple earth models these values are
            satisfactory.
        :type minRadius: float
        :param minRadius: Minimum radius of the model (km).
        :type maxRadius: float
        :param maxRadius: Maximum radius of the model (km).
        :type isSpherical: bool
        :param isSpherical: Is this a spherical model? Defaults to true.
        """
        self.modelName = modelName
        self.radiusOfEarth = radiusOfEarth
        self.mohoDepth = mohoDepth
        self.cmbDepth = cmbDepth
        self.iocbDepth = iocbDepth
        self.minRadius = minRadius
        self.maxRadius = maxRadius
        self.isSpherical = isSpherical
        self.layers = layers if layers else []

    def __len__(self):
        return len(self.layers)

    def getDisconDepths(self):
        """
        Returns the depths of discontinuities within the velocity model.
        """
        discontinuities = []

        discontinuities.append(self.layers[0].topDepth)
        for above_layer, below_layer in itertools.izip(self.layers[:-1],
                                                       self.layers[1:]):
            if above_layer.botPVelocity != below_layer.topPVelocity or \
                    above_layer.botSVelocity != below_layer.topSVelocity:
                # Discontinuity found.
                discontinuities.append(above_layer.botDepth)
        discontinuities.append(self.layers[-1].botDepth)

        return discontinuities

    def layerNumberAbove(self, depth):
        """
        Finds the layer containing the given depth. Note this returns the upper
        layer if the depth happens to be at a layer boundary.

        :returns: the layer number
        """
        for i, layer in enumerate(self.layers):
            if layer.topDepth < depth <= layer.botDepth:
                return i
        raise TauPException("No such layer.")

    def layerNumberBelow(self, depth):
        """
        Finds the layer containing the given depth. Note this returns the lower
        layer if the depth happens to be at a layer boundary.

        :returns: the layer number
        """
        for i, layer in enumerate(self.layers):
            if layer.topDepth <= depth < layer.botDepth:
                return i
        raise TauPException("No such layer.")


    def evaluateAbove(self, depth, materialProperty):
        """
        returns the value of the given material property, usually P or S
        velocity, at the given depth. Note this returns the value at the bottom
        of the upper layer if the depth happens to be at a layer boundary.

        :returns: the value of the given material property
        """
        layer = self.layers[self.layerNumberAbove(depth)]
        return layer.evaluateAt(depth, materialProperty)

    #
    #      * returns the value of the given material property, usually P or S
    #      * velocity, at the given depth. Note this returns the value at the top of
    #      * the lower layer if the depth happens to be at a layer boundary.
    #      *
    #      * @return the value of the given material property
    #      * @exception NoSuchLayerException
    #      *                occurs if no layer contains the given depth.
    #      * @exception NoSuchMatPropException
    #      *                occurs if the material property is not recognized.
    #
    def evaluateBelow(self, depth, materialProperty):
        """ generated source for method evaluateBelow """
        tempLayer = VelocityLayer()
        tempLayer = self.getVelocityLayer(self.layerNumberBelow(depth))
        return tempLayer.evaluateAt(depth, materialProperty)

    #
    #      * returns the value of the given material property, usually P or S
    #      * velocity, at the top of the given layer.
    #      *
    #      * @return the value of the given material property
    #      * @exception NoSuchMatPropException
    #      *                occurs if the material property is not recognized.
    #
    def evaluateAtTop(self, layerNumber, materialProperty):
        """ generated source for method evaluateAtTop """
        tempLayer = VelocityLayer()
        tempLayer = self.getVelocityLayer(layerNumber)
        return tempLayer.evaluateAtTop(materialProperty)

    #
    #      * returns the value of the given material property, usually P or S
    #      * velocity, at the bottom of the given layer.
    #      *
    #      * @return the value of the given material property
    #      * @exception NoSuchMatPropException
    #      *                occurs if the material property is not recognized.
    #
    def evaluateAtBottom(self, layerNumber, materialProperty):
        """ generated source for method evaluateAtBottom """
        tempLayer = VelocityLayer()
        tempLayer = self.getVelocityLayer(layerNumber)
        return tempLayer.evaluateAtBottom(materialProperty)

    #
    #      * returns the depth at the top of the given layer.
    #      *
    #      * @return the depth.
    #
    def depthAtTop(self, layerNumber):
        """ generated source for method depthAtTop """
        tempLayer = VelocityLayer()
        tempLayer = self.getVelocityLayer(layerNumber)
        return tempLayer.getTopDepth()

    #
    #      * returns the depth at the bottom of the given layer.
    #      *
    #      * @return the depth.
    #      * @exception NoSuchMatPropException
    #      *                occurs if the material property is not recognized.
    #
    def depthAtBottom(self, layerNumber):
        """ generated source for method depthAtBottom """
        tempLayer = VelocityLayer()
        tempLayer = self.getVelocityLayer(layerNumber)
        return tempLayer.getBotDepth()

    #
    #      * replaces layers in the velocity model with new layers. The number of old
    #      * and new layers need not be the same. @param matchTop false if the top
    #      * should be a discontinuity, true if the top velocity should be forced to
    #      * match the existing velocity at the top. @param matchBot similar for the
    #      * bottom.
    #
    def replaceLayers(self, newLayers, name, matchTop, matchBot):
        """ generated source for method replaceLayers """
        topLayerNum = self.layerNumberBelow(newLayers[0].getTopDepth())
        topLayer = self.getVelocityLayer(topLayerNum)
        botLayerNum = self.layerNumberAbove(newLayers[len(newLayers)].getBotDepth())
        botLayer = self.getVelocityLayer(botLayerNum)
        outLayers = ArrayList()
        outLayers.addAll(self.layer)
        try:
            if matchTop:
                newLayers[0] = VelocityLayer(newLayers[0].getLayerNum(), newLayers[0].getTopDepth(), newLayers[0].getBotDepth(), topLayer.evaluateAt(newLayers[0].getTopDepth(), 'P'), newLayers[0].getBotPVelocity(), topLayer.evaluateAt(newLayers[0].getTopDepth(), 'S'), newLayers[0].getBotSVelocity(), newLayers[0].getTopDensity(), newLayers[0].getBotDensity(), newLayers[0].getTopQp(), newLayers[0].getBotQp(), newLayers[0].getTopQs(), newLayers[0].getBotQs())
            if matchBot:
                newLayers[len(newLayers)] = VelocityLayer(end.getLayerNum(), end.getTopDepth(), end.getBotDepth(), end.getTopPVelocity(), botLayer.evaluateAt(newLayers[len(newLayers)].getBotDepth(), 'P'), end.getTopSVelocity(), botLayer.evaluateAt(newLayers[len(newLayers)].getBotDepth(), 'S'), end.getTopDensity(), end.getBotDensity(), end.getTopQp(), end.getBotQp(), end.getTopQs(), end.getBotQs())
        except NoSuchMatPropException as e:
            raise RuntimeException(e)
        if topLayer.getBotDepth() > newLayers[0].getTopDepth():
            try:
                topLayer = VelocityLayer(topLayer.getLayerNum(), topLayer.getTopDepth(), newLayers[0].getTopDepth(), topLayer.getTopPVelocity(), topLayer.evaluateAt(newLayers[0].getTopDepth(), 'P'), topLayer.getTopSVelocity(), topLayer.evaluateAt(newLayers[0].getTopDepth(), 'S'), topLayer.getTopDensity(), topLayer.getBotDensity())
                outLayers.set(topIndex, topLayer)
            except NoSuchMatPropException as e:
                raise RuntimeException(e)
            newVLayer.setTopPVelocity(topLayer.getBotPVelocity())
            newVLayer.setTopSVelocity(topLayer.getBotSVelocity())
            newVLayer.setTopDepth(topLayer.getBotDepth())
            outLayers.add(topLayerNum + 1, newVLayer)
            botLayerNum += 1
            topLayerNum += 1
        if botLayer.getBotDepth() > newLayers[len(newLayers)].getBotDepth():
            try:
                botLayer.setBotPVelocity(botLayer.evaluateAt(newLayers[len(newLayers)].getBotDepth(), 'P'))
                botLayer.setBotSVelocity(botLayer.evaluateAt(newLayers[len(newLayers)].getBotDepth(), 'S'))
                botLayer.setBotDepth(newLayers[len(newLayers)].getBotDepth())
            except NoSuchMatPropException as e:
                System.err.println("Caught NoSuchMatPropException: " + e.getMessage())
                e.printStackTrace()
            newVLayer.setTopPVelocity(botLayer.getBotPVelocity())
            newVLayer.setTopSVelocity(botLayer.getBotSVelocity())
            newVLayer.setTopDepth(botLayer.getBotDepth())
            outLayers.add(botLayerNum + 1, newVLayer)
            botLayerNum += 1
        i = topLayerNum
        while i <= botLayerNum:
            outLayers.remove(topLayerNum)
            i += 1
        i = 0
        while len(newLayers):
            outLayers.add(topLayerNum + i, newLayers[i])
            i += 1
        outVMod = VelocityModel(name, self.getRadiusOfEarth(), self.getMohoDepth(), self.getCmbDepth(), self.getIocbDepth(), self.getMinRadius(), self.getMaxRadius(), self.getSpherical(), outLayers)
        outVMod.fixDisconDepths()
        outVMod.validate()
        return outVMod

    @overloaded
    def printGMT(self, filename):
        """ generated source for method printGMT """
        psFile = str()
        if filename.endsWith(".gmt"):
            psFile = filename.substring(0, 4 - len(filename)) + ".ps"
        else:
            psFile = filename + ".ps"
        dos = PrintWriter(BufferedWriter(FileWriter(filename)))
        dos.println("#!/bin/sh")
        dos.println("#\n# This script will plot the " + self.getModelName() + " velocity model using GMT. If you want to\n" + "#use this as a data file for psxy in another script, delete these" + "\n# first lines, as well as the last line.\n#")
        dos.println("/bin/rm -f " + psFile + "\n")
        maxVel = 0
        for vLayer in layer:
            if vLayer.getTopPVelocity() > maxVel:
                maxVel = vLayer.getTopPVelocity()
            if vLayer.getBotPVelocity() > maxVel:
                maxVel = vLayer.getBotPVelocity()
            if vLayer.getTopSVelocity() > maxVel:
                maxVel = vLayer.getTopSVelocity()
            if vLayer.getBotSVelocity() > maxVel:
                maxVel = vLayer.getBotSVelocity()
        maxVel *= 1.05
        dos.println("PCOLOR=0/0/255")
        dos.println("SCOLOR=255/0/0")
        dos.println()
        dos.println("psbasemap -JX6i/-9i -P -R0/" + maxVel + "/0/" + self.getMaxRadius() + " -B1a2:'Velocity (km/s)':/200a400:'Depth (km)':/:.'" + self.getModelName() + "':WSen  -K > " + psFile)
        dos.println()
        dos.println("psxy -JX -P -R -W2p,${PCOLOR} -: -m -O -K >> " + psFile + " <<END")
        printGMTforP(dos)
        dos.println("END\n")
        dos.println("psxy -JX -P -R -W2p,${SCOLOR} -: -m -O >> " + psFile + " <<END")
        printGMTforS(dos)
        dos.println("END\n")
        dos.close()

    @printGMT.register(object, PrintWriter)
    def printGMT_0(self, dos):
        """ generated source for method printGMT_0 """
        dos.println("> P velocity for " + self.modelName + "  below")
        printGMTforP(dos)
        dos.println("> S velocity for " + self.modelName + "  below")
        printGMTforP(dos)

    def printGMTforP(self, dos):
        """ generated source for method printGMTforP """
        pVel = -1.0
        layerNum = 0
        while layerNum < self.getNumLayers():
            if currVelocityLayer.getTopPVelocity() != pVel:
                dos.println(float(currVelocityLayer.getTopDepth()) + " " + float(currVelocityLayer.getTopPVelocity()))
            dos.println(float(currVelocityLayer.getBotDepth()) + " " + float(currVelocityLayer.getBotPVelocity()))
            pVel = currVelocityLayer.getBotPVelocity()
            layerNum += 1

    def printGMTforS(self, dos):
        """ generated source for method printGMTforS """
        sVel = -1.0
        layerNum = 0
        while layerNum < self.getNumLayers():
            if currVelocityLayer.getTopSVelocity() != sVel:
                dos.println(float(currVelocityLayer.getTopDepth()) + " " + float(currVelocityLayer.getTopSVelocity()))
            dos.println(float(currVelocityLayer.getBotDepth()) + " " + float(currVelocityLayer.getBotSVelocity()))
            sVel = currVelocityLayer.getBotSVelocity()
            layerNum += 1

    def validate(self):
        """ generated source for method validate """
        currVelocityLayer = VelocityLayer()
        prevVelocityLayer = VelocityLayer()
        if self.radiusOfEarth <= 0.0:
            System.err.println("Radius of earth is not positive. radiusOfEarth = " + self.radiusOfEarth)
            return False
        if self.mohoDepth < 0.0:
            System.err.println("mohoDepth is not non-negative. mohoDepth = " + self.mohoDepth)
            return False
        if self.cmbDepth < self.mohoDepth:
            System.err.println("cmbDepth < mohoDepth. cmbDepth = " + self.cmbDepth + " mohoDepth = " + self.mohoDepth)
            return False
        if self.cmbDepth <= 0.0:
            System.err.println("cmbDepth is not positive. cmbDepth = " + self.cmbDepth)
            return False
        if self.iocbDepth < self.cmbDepth:
            System.err.println("iocbDepth < cmbDepth. iocbDepth = " + self.iocbDepth + " cmbDepth = " + self.cmbDepth)
            return False
        if self.iocbDepth <= 0.0:
            System.err.println("iocbDepth is not positive. iocbDepth = " + self.iocbDepth)
            return False
        if self.minRadius < 0.0:
            System.err.println("minRadius is not non-negative. minRadius = " + self.minRadius)
            return False
        if self.maxRadius <= 0.0:
            System.err.println("maxRadius is not positive. maxRadius = " + self.maxRadius)
            return False
        if self.maxRadius <= self.minRadius:
            System.err.println("maxRadius <= minRadius. maxRadius = " + self.maxRadius + " minRadius = " + self.minRadius)
            return False
        currVelocityLayer = self.getVelocityLayer(0)
        prevVelocityLayer = VelocityLayer(0, currVelocityLayer.getTopDepth(), currVelocityLayer.getTopDepth(), currVelocityLayer.getTopPVelocity(), currVelocityLayer.getTopPVelocity(), currVelocityLayer.getTopSVelocity(), currVelocityLayer.getTopSVelocity(), currVelocityLayer.getTopDensity(), currVelocityLayer.getTopDensity())
        layerNum = 0
        while layerNum < self.getNumLayers():
            currVelocityLayer = self.getVelocityLayer(layerNum)
            if prevVelocityLayer.getBotDepth() != currVelocityLayer.getTopDepth():
                System.err.println("There is a gap in the velocity model " + "between layers " + (layerNum - 1) + " and " + layerNum)
                System.err.println("prevVelocityLayer=" + prevVelocityLayer)
                System.err.println("currVelocityLayer=" + currVelocityLayer)
                return False
            if currVelocityLayer.getBotDepth() == currVelocityLayer.getTopDepth():
                System.err.println("There is a zero thickness layer in the " + "velocity model at layer " + layerNum)
                System.err.println("prevVelocityLayer=" + prevVelocityLayer)
                System.err.println("currVelocityLayer=" + currVelocityLayer)
                return False
            if currVelocityLayer.getTopPVelocity() <= 0.0 or currVelocityLayer.getBotPVelocity() <= 0.0:
                System.err.println("There is a negative P velocity layer in the " + "velocity model at layer " + layerNum)
                return False
            if currVelocityLayer.getTopSVelocity() < 0.0 or currVelocityLayer.getBotSVelocity() < 0.0:
                System.err.println("There is a negative S velocity layer in the " + "velocity model at layer " + layerNum)
                return False
            if (currVelocityLayer.getTopPVelocity() != 0.0 and currVelocityLayer.getBotPVelocity() == 0.0) or (currVelocityLayer.getTopPVelocity() == 0.0 and currVelocityLayer.getBotPVelocity() != 0.0):
                System.err.println("There is a layer that goes to zero P velocity " + "without a discontinuity in the " + "velocity model at layer " + layerNum + "\nThis would cause a divide by zero within this " + "depth range. Try making the velocity small, followed by a " + "discontinuity to zero velocity.")
                return False
            if (currVelocityLayer.getTopSVelocity() != 0.0 and currVelocityLayer.getBotSVelocity() == 0.0) or (currVelocityLayer.getTopSVelocity() == 0.0 and currVelocityLayer.getBotSVelocity() != 0.0):
                System.err.println("There is a layer that goes to zero S velocity " + "without a discontinuity in the " + "velocity model at layer " + layerNum + "\nThis would cause a divide by zero within this " + "depth range. Try making the velocity small, followed by a " + "discontinuity to zero velocity.")
                return False
            prevVelocityLayer = currVelocityLayer
            layerNum += 1
        return True

    def __str__(self):
        """ generated source for method toString """
        desc = "modelName=" + self.modelName + "\n" + "\n radiusOfEarth=" + self.radiusOfEarth + "\n mohoDepth=" + self.mohoDepth + "\n cmbDepth=" + self.cmbDepth + "\n iocbDepth=" + self.iocbDepth + "\n minRadius=" + self.minRadius + "\n maxRadius=" + self.maxRadius + "\n spherical=" + self.spherical
        desc += "\ngetNumLayers()=" + self.getNumLayers() + "\n"
        return desc

    def print_(self):
        """ generated source for method print_ """
        i = 0
        while i < self.getNumLayers():
            print self.getVelocityLayer(i)
            i += 1

    @classmethod
    def getModelNameFromFileName(cls, filename):
        """ generated source for method getModelNameFromFileName """
        j = filename.lastIndexOf(System.getProperty("file.separator"))
        modelFilename = filename.substring(j + 1)
        modelName = modelFilename
        if modelFilename.endsWith("tvel"):
            modelName = modelFilename.substring(0, 5 - len(modelFilename))
        elif modelFilename.endsWith(".nd"):
            modelName = modelFilename.substring(0, 3 - len(modelFilename))
        elif modelFilename.startsWith("GB."):
            modelName = modelFilename.substring(3, len(modelFilename))
        else:
            modelName = modelFilename
        return modelName

    @classmethod
    def readVelocityFile(cls, filename, fileType):
        """ generated source for method readVelocityFile """
        if fileType == None or fileType == "":
            if filename.endsWith(".nd"):
                fileType = ".nd"
            elif filename.endsWith(".tvel"):
                fileType = ".tvel"
        if fileType.startsWith("."):
            fileType = fileType.substring(1, len(fileType))
        f = File(filename)
        if not f.exists() and not filename.endsWith("." + fileType) and File(filename + "." + fileType).exists():
            f = File(filename + "." + fileType)
        vMod = VelocityModel()
        if fileType.lower() == "nd".lower():
            vMod = readNDFile(f)
        elif fileType.lower() == "tvel".lower():
            vMod = readTVelFile(f)
        else:
            raise VelocityModelException("What type of velocity file, .tvel or .nd?")
        vMod.fixDisconDepths()
        return vMod

    @classmethod
    @overloaded
    def readTVelFile(cls, file_):
        """ generated source for method readTVelFile """
        fileIn = FileReader(file_)
        vmod = cls.readTVelFile(fileIn, cls.getModelNameFromFileName(file_.__name__))
        fileIn.close()
        return vmod

    @classmethod
    @readTVelFile.register(object, Reader, str)
    def readTVelFile_0(cls, in_, modelName):
        """ generated source for method readTVelFile_0 """
        tokenIn = StreamTokenizer(in_)
        tokenIn.commentChar('#')
        tokenIn.slashStarComments(True)
        tokenIn.slashSlashComments(True)
        tokenIn.eolIsSignificant(True)
        tokenIn.parseNumbers()
        while tokenIn.nextToken() != StreamTokenizer.TT_EOL:
            pass
        while tokenIn.nextToken() != StreamTokenizer.TT_EOL:
            pass
        myLayerNumber = 0
        tempLayer = VelocityLayer()
        topDepth = float()
        topPVel = float()
        topSVel = float()
        topDensity = float()
        botDepth = float()
        botPVel = float()
        botSVel = float()
        botDensity = float()
        tokenIn.nextToken()
        topDepth = tokenIn.nval
        tokenIn.nextToken()
        topPVel = tokenIn.nval
        tokenIn.nextToken()
        topSVel = tokenIn.nval
        if topSVel > topPVel:
            raise VelocityModelException("S velocity, " + topSVel + " at depth " + topDepth + " is greater than the P velocity, " + topPVel)
        tokenIn.nextToken()
        if tokenIn.ttype != StreamTokenizer.TT_EOL:
            topDensity = tokenIn.nval
            tokenIn.nextToken()
        else:
            topDensity = 5571.0
        if tokenIn.ttype != StreamTokenizer.TT_EOL:
            raise VelocityModelException("Should have found an EOL but didn't" + " Layer=" + myLayerNumber + " tokenIn=" + tokenIn)
        else:
            tokenIn.nextToken()
        layers = ArrayList()
        while tokenIn.ttype != StreamTokenizer.TT_EOF:
            botDepth = tokenIn.nval
            tokenIn.nextToken()
            botPVel = tokenIn.nval
            tokenIn.nextToken()
            botSVel = tokenIn.nval
            if botSVel > botPVel:
                raise VelocityModelException("S velocity, " + botSVel + " at depth " + botDepth + " is greater than the P velocity, " + botPVel)
            tokenIn.nextToken()
            if tokenIn.ttype != StreamTokenizer.TT_EOL:
                botDensity = tokenIn.nval
                tokenIn.nextToken()
            else:
                botDensity = topDensity
            tempLayer = VelocityLayer(myLayerNumber, topDepth, botDepth, topPVel, botPVel, topSVel, botSVel, topDensity, botDensity)
            topDepth = botDepth
            topPVel = botPVel
            topSVel = botSVel
            topDensity = botDensity
            if tokenIn.ttype != StreamTokenizer.TT_EOL:
                raise VelocityModelException("Should have found an EOL but didn't" + " Layer=" + myLayerNumber + " tokenIn=" + tokenIn)
            else:
                tokenIn.nextToken()
            if tempLayer.getTopDepth() != tempLayer.getBotDepth():
                layers.add(tempLayer)
                myLayerNumber += 1
        radiusOfEarth = topDepth
        maxRadius = topDepth
        return VelocityModel(modelName, radiusOfEarth, cls.DEFAULT_MOHO, cls.DEFAULT_CMB, cls.DEFAULT_IOCB, 0, maxRadius, True, layers)

    @classmethod
    @overloaded
    def readNDFile(cls, file_):
        """ generated source for method readNDFile """
        fileIn = FileReader(file_)
        vmod = cls.readNDFile(fileIn, cls.getModelNameFromFileName(file_.__name__))
        fileIn.close()
        return vmod

    @classmethod
    @readNDFile.register(object, Reader, str)
    def readNDFile_0(cls, in_, modelName):
        """ generated source for method readNDFile_0 """
        tokenIn = StreamTokenizer(in_)
        tokenIn.commentChar('#')
        tokenIn.slashStarComments(True)
        tokenIn.slashSlashComments(True)
        tokenIn.eolIsSignificant(True)
        tokenIn.parseNumbers()
        myLayerNumber = 0
        tempLayer = VelocityLayer()
        topDepth = float()
        topPVel = float()
        topSVel = float()
        topDensity = 2.6
        topQp = 1000
        topQs = 2000
        botDepth = float()
        botPVel = float()
        botSVel = float()
        botDensity = topDensity
        botQp = topQp
        botQs = topQs
        tokenIn.nextToken()
        topDepth = tokenIn.nval
        tokenIn.nextToken()
        topPVel = tokenIn.nval
        tokenIn.nextToken()
        topSVel = tokenIn.nval
        if topSVel > topPVel:
            raise VelocityModelException("S velocity, " + topSVel + " at depth " + topDepth + " is greater than the P velocity, " + topPVel)
        tokenIn.nextToken()
        if tokenIn.ttype != StreamTokenizer.TT_EOL:
            topDensity = tokenIn.nval
            tokenIn.nextToken()
            if tokenIn.ttype != StreamTokenizer.TT_EOL:
                topQp = tokenIn.nval
                tokenIn.nextToken()
                if tokenIn.ttype != StreamTokenizer.TT_EOL:
                    topQs = tokenIn.nval
                    tokenIn.nextToken()
        if tokenIn.ttype != StreamTokenizer.TT_EOL:
            raise VelocityModelException("Should have found an EOL but didn't" + " Layer=" + myLayerNumber + " tokenIn=" + tokenIn)
        else:
            tokenIn.nextToken()
        mohoDepth = cls.DEFAULT_MOHO
        cmbDepth = cls.DEFAULT_CMB
        iocbDepth = cls.DEFAULT_IOCB
        layers = ArrayList()
        while tokenIn.ttype != StreamTokenizer.TT_EOF:
            if tokenIn.ttype == StreamTokenizer.TT_WORD:
                if tokenIn.sval.lower() == "mantle".lower() or tokenIn.sval.lower() == "moho".lower():
                    mohoDepth = topDepth
                if tokenIn.sval.lower() == "outer-core".lower() or tokenIn.sval.lower() == "cmb".lower():
                    cmbDepth = topDepth
                if tokenIn.sval.lower() == "inner-core".lower() or tokenIn.sval.lower() == "icocb".lower():
                    iocbDepth = topDepth
                while tokenIn.ttype != StreamTokenizer.TT_EOL:
                    tokenIn.nextToken()
                tokenIn.nextToken()
                continue
            botDepth = tokenIn.nval
            tokenIn.nextToken()
            botPVel = tokenIn.nval
            tokenIn.nextToken()
            botSVel = tokenIn.nval
            if botSVel > botPVel:
                raise VelocityModelException("S velocity, " + botSVel + " at depth " + botDepth + " is greater than the P velocity, " + botPVel)
            tokenIn.nextToken()
            if tokenIn.ttype != StreamTokenizer.TT_EOL:
                botDensity = tokenIn.nval
                tokenIn.nextToken()
                if tokenIn.ttype != StreamTokenizer.TT_EOL:
                    botQp = tokenIn.nval
                    tokenIn.nextToken()
                    if tokenIn.ttype != StreamTokenizer.TT_EOL:
                        botQs = tokenIn.nval
                        tokenIn.nextToken()
            tempLayer = VelocityLayer(myLayerNumber, topDepth, botDepth, topPVel, botPVel, topSVel, botSVel, topDensity, botDensity, topQp, botQp, topQs, botQs)
            topDepth = botDepth
            topPVel = botPVel
            topSVel = botSVel
            topDensity = botDensity
            topQp = botQp
            topQs = botQs
            if tokenIn.ttype != StreamTokenizer.TT_EOL:
                raise VelocityModelException("Should have found an EOL but didn't" + " Layer=" + myLayerNumber + " tokenIn=" + tokenIn)
            else:
                tokenIn.nextToken()
            if tempLayer.getTopDepth() != tempLayer.getBotDepth():
                layers.add(tempLayer)
                myLayerNumber += 1
        radiusOfEarth = topDepth
        maxRadius = topDepth
        return VelocityModel(modelName, radiusOfEarth, mohoDepth, cmbDepth, iocbDepth, 0, maxRadius, True, layers)

    def fixDisconDepths(self):
        """ generated source for method fixDisconDepths """
        changeMade = False
        aboveLayer = VelocityLayer()
        belowLayer = VelocityLayer()
        mohoMin = 65.0
        cmbMin = self.radiusOfEarth
        iocbMin = self.radiusOfEarth - 100.0
        tempMohoDepth = 0.0
        tempCmbDepth = self.radiusOfEarth
        tempIocbDepth = self.radiusOfEarth
        layerNum = 0
        while layerNum < self.getNumLayers() - 1:
            aboveLayer = self.getVelocityLayer(layerNum)
            belowLayer = self.getVelocityLayer(layerNum + 1)
            if aboveLayer.getBotPVelocity() != belowLayer.getTopPVelocity() or aboveLayer.getBotSVelocity() != belowLayer.getTopSVelocity():
                if Math.abs(self.mohoDepth - aboveLayer.getBotDepth()) < mohoMin:
                    tempMohoDepth = aboveLayer.getBotDepth()
                    mohoMin = Math.abs(self.mohoDepth - aboveLayer.getBotDepth())
                if Math.abs(self.cmbDepth - aboveLayer.getBotDepth()) < cmbMin:
                    tempCmbDepth = aboveLayer.getBotDepth()
                    cmbMin = Math.abs(self.cmbDepth - aboveLayer.getBotDepth())
                if aboveLayer.getBotSVelocity() == 0.0 and belowLayer.getTopSVelocity() > 0.0 and Math.abs(self.iocbDepth - aboveLayer.getBotDepth()) < iocbMin:
                    tempIocbDepth = aboveLayer.getBotDepth()
                    iocbMin = Math.abs(self.iocbDepth - aboveLayer.getBotDepth())
            layerNum += 1
        if self.mohoDepth != tempMohoDepth or self.cmbDepth != tempCmbDepth or self.iocbDepth != tempIocbDepth:
            changeMade = True
        self.mohoDepth = tempMohoDepth
        self.cmbDepth = tempCmbDepth
        self.iocbDepth = (tempIocbDepth if tempCmbDepth != tempIocbDepth else self.radiusOfEarth)
        return changeMade

    def earthFlattenTransform(self):
        """ generated source for method earthFlattenTransform """
        newLayer = VelocityLayer()
        oldLayer = VelocityLayer()
        spherical = False
        layers = ArrayList(self.vectorLength)
        i = 0
        while i < self.getNumLayers():
            oldLayer = self.getVelocityLayer(i)
            newLayer = VelocityLayer(i, self.radiusOfEarth * Math.log(oldLayer.getTopDepth() / self.radiusOfEarth), self.radiusOfEarth * Math.log(oldLayer.getBotDepth() / self.radiusOfEarth), self.radiusOfEarth * oldLayer.getTopPVelocity() / oldLayer.getTopDepth(), self.radiusOfEarth * oldLayer.getBotPVelocity() / oldLayer.getBotDepth(), self.radiusOfEarth * oldLayer.getTopSVelocity() / oldLayer.getTopDepth(), self.radiusOfEarth * oldLayer.getBotSVelocity() / oldLayer.getBotDepth())
            layers.add(newLayer)
            i += 1
        return VelocityModel(self.modelName, self.getRadiusOfEarth(), self.getMohoDepth(), self.getCmbDepth(), self.getIocbDepth(), self.getMinRadius(), self.getMaxRadius(), spherical, layers)
