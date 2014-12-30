import os
import shutil
import logging
from golem.environments.Environment import Environment
from examples.gnr.task.ThreeDSMaxCfgEditor import regenerateFile

logger = logging.getLogger(__name__)

class ThreeDSMaxEnvironment( Environment ):
    @classmethod
    def getId( cls ):
        return "3DSMAX"

    def __init__( self ):
        Environment.__init__( self )
        self.software.append('3DS Max Studio 2015')
        self.software.append('Windows')
        self.softwareEnvVar = ['ADSK_3DSMAX_x64_2015', 'ADSK_3DSMAX_x32_2015']
        self.softwareName = '3dsmaxcmd.exe'
        self.configFileName = 'plugcfg_ln/mentalray_cpu.ini'
        self.configFileBackup = 'plugcfg_ln/mentalray_cpu.bak'
        self.shortDescription = "3DS MAX Studio command tool (http://www.autodesk.pl/products/3ds-max/overview)"
        self.path = ""

    def checkSoftware( self ):
        for var in self.softwareEnvVar:
            if os.environ.get( var ):
                self.path = os.path.join( os.environ.get( var ), '3dsmaxcmd.exe')
                if os.path.isfile( self.path ):
                    return True
        return False

    def supported( self ) :
        return self.checkSoftware()

    def get3dsmaxcmdPath ( self ):
        self.checkSoftware()
        if os.path.isfile( self.path ):
            return self.path
        else:
            return ""

    def setNThreads( self, numCores ):
        for var in self.softwareEnvVar:
            if os.environ.get( var ):
                self.__rewriteCfgFile( var, numCores)


    def __rewriteCfgFile( self, var, numCores ):
        path = os.path.join( os.environ.get( var ), self.configFileName )
        backupPath = os.path.join( os.environ.get( var ), self.configFileBackup )
        logger.debug("Cfg file: {}, numThreads = {}".format( path, numCores ))
        if os.path.isfile( path ):
            with open( path, 'r') as f:
                cfgSrc = f.read()
            shutil.copy2( path, backupPath )
            newCfg = regenerateFile( cfgSrc, numCores )
            with open(path, 'w') as f:
                f.write( newCfg )
            return


    def getDefaultPreset( self ):
        for var in self.softwareEnvVar:
            if os.environ.get( var ):
                presetFile = os.path.join( os.environ.get( var ), 'renderpresets\mental.ray.daylighting.high.rps' )
                if os.path.isfile( presetFile ):
                    return presetFile
        return ""


class PBRTEnvironment ( Environment ):
    @classmethod
    def getId( cls ):
        return "PBRT"

    def __init__( self ):
        Environment.__init__( self )
        self.software.append('Windows')
        self.shortDescription =  "PBRT renderer (http://www.pbrt.org/)  "

    def supported( self ) :
        return True

class VRayEnvironment( Environment ):
    @classmethod
    def getId( cls ):
        return "VRAY"

    def __init__( self ):
        Environment.__init__( self )
        self.software.append('Windows')
        self.software.append('V-Ray standalone')
        self.shortDescription = "V-Ray Renderer (http://www.vray.com/)"
        self.softwareEnvVariable = 'VRAY_PATH'
        self.softwareName = 'vray.exe'
        self.path = ""

    def checkSoftware( self ):
        if os.environ.get( self.softwareEnvVariable ):
            self.path = os.path.join( os.environ.get( self.softwareEnvVariable ), self.softwareName )
            if os.path.isfile( self.path ):
                return True
        return False

    def supported( self ):
        return self.checkSoftware()

    def getCmdPath ( self ):
        self.checkSoftware()
        if os.path.isfile( self.path ):
            return self.path
        else:
            return ""

