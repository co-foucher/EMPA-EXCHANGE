session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

session.graphicsOptions.setValues(backgroundColor='#FFFFFF')

from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
import connectorBehavior
import time
from abaqus import getInputs
from abaqus import getInput
import os

from abaqus import *
from abaqusConstants import *


# this is the setup  for where the files are

input_name = "inp_material-c2_f0p6_MaterialEdited_remeshed"
output_name = "inp_material-c2_f0p6_impact"

current_dir = "D:/COFO - HP/01 PhD research/202403 - Bern skull/WP5 - bern-001/03 - Simulation Setup/036 - contact-step"
parent_dir = os.path.dirname(current_dir)
os.chdir(current_dir)
print(f"working in directory: {current_dir}")

mdb.ModelFromInputFile(name=input_name, 
    inputFileName=parent_dir + '/035 - repair mesh/' + input_name + '.inp')

model_name = "inp_material-c2_f0p6_MaterialEdited_re"
part_name = mdb.models[model_name].parts.keys()[-1]


print(' ')
print(' ')
print(' ')
print('===================================================================')
print('===================== starting model creation =====================')
print('===================================================================')


#===========================================================================================================================
#============================================== list of variables ==========================================================
#===========================================================================================================================

#model_name = mdb.models.keys()[-1]
part_name = mdb.models[model_name].parts.keys()[-1]


print('working on model' + model_name)
#===========================================================================================================================
#============================================== abaqus setup ==========================================================
#===========================================================================================================================


session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

session.graphicsOptions.setValues(backgroundStyle=SOLID, backgroundColor='#FFFFFF')


#===========================================================================================================================
#============================================== STEP setup ==========================================================
#===========================================================================================================================
print('===================== STEP setup =====================')

mdb.models[model_name].ExplicitDynamicsStep(name='Step-1', 
    previous='Initial', timePeriod=0.002, improvedDtMethod=ON, scaleFactor=0.95)

mdb.models[model_name].fieldOutputRequests['F-Output-1'].setValues(
    variables=('S', 'SVAVG', 'MISES', 'E', 'PE', 'PEVAVG', 'PEEQ', 'PEEQVAVG', 
    'LE', 'U', 'V', 'A', 'RF', 'CSTRESS', 'EVF'), numIntervals=500, 
    position=INTEGRATION_POINTS)

mdb.models[model_name].historyOutputRequests['H-Output-1'].setValues(
    numIntervals=500)

print('step created')

#===========================================================================================================================
#============================================== assembly setup ==========================================================
#===========================================================================================================================
print('===================== assembly setup =====================')

# ======== MAKE THE PLAQUASSE
s = mdb.models[model_name].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.rectangle(point1=(-200, -200), point2=(200, 200))
p = mdb.models[model_name].Part(name='la-plaquasse', 
    dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models[model_name].parts['la-plaquasse']
p.BaseSolidExtrude(sketch=s, depth=2.0)
s.unsetPrimaryObject()

p = mdb.models[model_name].parts['la-plaquasse']
p.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models[model_name].parts['la-plaquasse']
p.generateMesh()


cells = mdb.models[model_name].parts['la-plaquasse'].cells.findAt(((0.0, 0, 0), ))
region = mdb.models[model_name].parts['la-plaquasse'].Set(cells=cells, name='Set-whole_plaquasse')

mdb.models[model_name].Material(name='plaquasse')
mdb.models[model_name].materials['plaquasse'].Density(table=((float(float(1)), ), ))
mdb.models[model_name].materials['plaquasse'].Elastic(table=((float(1e6), float(0.3)), ))
mdb.models[model_name].HomogeneousSolidSection(material='plaquasse', name='Section-plaquasse', thickness=None)

mdb.models[model_name].parts['la-plaquasse'].SectionAssignment(
    offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, 
    region=mdb.models[model_name].parts['la-plaquasse'].sets['Set-whole_plaquasse'], 
    sectionName='Section-plaquasse', 
    thicknessAssignment=FROM_SECTION)

print('plaquasse created')
# ======== make assembly

a = mdb.models[model_name].rootAssembly
p = mdb.models[model_name].parts['la-plaquasse']
a.Instance(name='la-plaquasse-1', part=p, dependent=ON)
p1 = a.instances['la-plaquasse-1']
p1.translate(vector=(600, 0.0, 0.0))

a.rotate(instanceList=('la-plaquasse-1', ), axisPoint=(0.0, 0.0, 0.0), 
    axisDirection=(10.0, 0.0, 0.0), angle=90.0)

a.translate(instanceList=('la-plaquasse-1', ), vector=(276.275421, 23.82069, 
    238.800705))
a.translate(instanceList=('la-plaquasse-1', ), vector=(0.0, -30.0, 0.0))

a.translate(instanceList=('la-plaquasse-1', ), vector=(-600.0, 0.0, 0.0))

a.translate(instanceList=('PART-1-1', ), vector=(0.0, -38.0, 0.0))

mdb.models[model_name].rootAssembly.translate(instanceList=('PART-1-1', 'la-plaquasse-1'), 
    vector=(-273.88504, -58.269494, -335.725797))

mdb.models[model_name].rootAssembly.rotate(angle=20.0, axisDirection=(
    1.0, 0.0, 0.0), axisPoint=(0.0, 0.0, 0.0), instanceList=('PART-1-1', ))

mdb.models[model_name].rootAssembly.rotate(angle=-10.0, axisDirection=(
    0.0, 1.0, 0.0), axisPoint=(0.0, 0.0, 0.0), instanceList=('PART-1-1', ))


print('assembly done')

#===========================================================================================================================
#============================================== load and BC setup ==========================================================
#===========================================================================================================================
print('===================== load setup =====================')

#============= initial velocity of skull
#elements = mdb.models[model_name].parts['PART-1'].elements[0:244572]
#mdb.models[model_name].parts['PART-1'].Set(elements=elements, name='Set-whole_skull')

nodes1 = mdb.models[model_name].rootAssembly.instances['PART-1-1'].nodes[0:65376]
a.Set(nodes=nodes1, name='Set-whole_skull_x')

mdb.models[model_name].Velocity(field='', distributionType=MAGNITUDE, 
    name='Predefined Field-1', omega=0.0, 
    region=mdb.models[model_name].rootAssembly.sets['Set-whole_skull_x'], 
    velocity1=0.0, velocity2=-11000.0, velocity3=0.0)

print('initial velocity done')

#================= pin the plaquasse

faces = mdb.models[model_name].parts['la-plaquasse'].faces.findAt(((0, 0, 2.0), ))
mdb.models[model_name].parts['la-plaquasse'].Set(faces=faces, name='Set-BC')

region = mdb.models[model_name].rootAssembly.instances['la-plaquasse-1'].sets['Set-BC']
mdb.models[model_name].PinnedBC(name='BC-1', createStepName='Initial', 
    region=region, localCsys=None)

#===========================================================================================================================
#============================================== added mass setup ==========================================================
#===========================================================================================================================
print('===================== added mass setup =====================')

#=============== some things must be done manually for now
#                       - the coupling

#=============== creating ref points
a = mdb.models[model_name].rootAssembly
a.ReferencePoint(point=(0.0, 50.0, 50.0))
a = mdb.models[model_name].rootAssembly
a.ReferencePoint(point=(0.0, 100.0, 50.0))

#=============== creating line
r11 = mdb.models[model_name].rootAssembly.referencePoints
mdb.models[model_name].rootAssembly.WirePolyLine(points=((r11[13], r11[14]), ), mergeType=IMPRINT, meshable=OFF)
e1 = mdb.models[model_name].rootAssembly.edges
edges1 = e1.findAt(((0.0, 62.5, 50.0), ))
mdb.models[model_name].rootAssembly.Set(edges=edges1, name='Wire-1-Set-1')

#=============== creating connector
mdb.models[model_name].ConnectorSection(name='ConnSect-1', assembledType=TRANSLATOR)
elastic_0 = connectorBehavior.ConnectorElasticity(components=(1, ), table=((1000000.0, ), ))
mdb.models[model_name].sections['ConnSect-1'].setValues(behaviorOptions = (elastic_0, ) )
mdb.models[model_name].sections['ConnSect-1'].behaviorOptions[0].ConnectorOptions()

edges1 = mdb.models[model_name].rootAssembly.edges.findAt(((0.0, 62.5, 50.0), ))
region=mdb.models[model_name].rootAssembly.Set(edges=edges1, name='Set-conector')
datum1 = mdb.models[model_name].rootAssembly.datums[9]
csa = mdb.models[model_name].rootAssembly.SectionAssignment(sectionName='ConnSect-1', region=region)
mdb.models[model_name].rootAssembly.ConnectorOrientation(angle1=90.0, axis1=AXIS_2, region=csa.getSet(), 
    localCsys1=datum1)

#=============== adding initial velocity
mdb.models[model_name].PredefinedField(name='Predefined Field-1-Copy', 
    objectToCopy=mdb.models[model_name].predefinedFields['Predefined Field-1'], 
    toStepName='Initial')

r1 = mdb.models[model_name].rootAssembly.referencePoints
refPoints1=(r1[13], r1[14], )
region = mdb.models[model_name].rootAssembly.Set(referencePoints=refPoints1, name='Set-2RF')
mdb.models[model_name].predefinedFields['Predefined Field-1-Copy'].setValues(
    region=region, velocity1=0.0, velocity2=-11000.0, velocity3=0.0, omega=0.0)

#=============== adding mass
r1 = mdb.models[model_name].rootAssembly.referencePoints
refPoints1=(r1[14], )
region=mdb.models[model_name].rootAssembly.Set(referencePoints=refPoints1, name='Set-addedmass')
mdb.models[model_name].rootAssembly.engineeringFeatures.PointMassInertia(
    name='Inertia-1', region=region, mass=0.3, i11=1.0, i22=1.0, i33=1.0, 
    alpha=0.0, composite=0.0)

#=============== adding BC
region = mdb.models[model_name].rootAssembly.sets['Set-2RF']
mdb.models[model_name].DisplacementBC(name='BC-2', 
    createStepName='Step-1', region=region, u1=0.0, u2=UNSET, u3=0.0, ur1=0.0, 
    ur2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, 
    fieldName='', localCsys=None)

print('mass added done')
print('WARNING: remember to add coupling to the added mass')

#===========================================================================================================================
#============================================== interactions setup ==========================================================
#===========================================================================================================================
print('===================== interactions setup =====================')

mdb.models[model_name].ContactProperty('IntProp-1')
mdb.models[model_name].interactionProperties['IntProp-1'].NormalBehavior(
    pressureOverclosure=LINEAR, contactStiffness=1000.0, 
    constraintEnforcementMethod=DEFAULT)
mdb.models[model_name].ContactExp(name='Int-1', createStepName='Step-1')
mdb.models[model_name].interactions['Int-1'].includedPairs.setValuesInStep(
    stepName='Step-1', useAllstar=ON)
mdb.models[model_name].interactions['Int-1'].contactPropertyAssignments.appendInStep(
    stepName='Step-1', assignments=((GLOBAL, SELF, 'IntProp-1'), ))

print('interactions done')

#===========================================================================================================================
#============================================== Job setup ==========================================================
#===========================================================================================================================
print('===================== Job setup =====================')

mdb.Job(activateLoadBalancing=False, atTime=None, contactPrint=OFF, 
    description='', echoPrint=OFF, explicitPrecision=DOUBLE, historyPrint=OFF, 
    memory=90, memoryUnits=PERCENTAGE, model=model_name, modelPrint=OFF, 
    multiprocessingMode=DEFAULT, name=output_name, nodalOutputPrecision=SINGLE, 
    numCpus=14, numDomains=14, parallelizationMethodExplicit=DOMAIN, 
    queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS, 
    userSubroutine='', waitHours=0, waitMinutes=0)

mdb.jobs[output_name].writeInput(consistencyChecking=OFF)

print('job created')



