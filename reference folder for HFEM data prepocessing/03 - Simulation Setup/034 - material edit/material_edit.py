########################### importing the required libraries
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
from connectorBehavior import *
import numpy as np
import time
import sys
import os
from abaqus import *
from abaqusConstants import *
from caeModules import *

list_of_models = ['inp_material-c1p75_f0p6',
	'inp_material-c1p75_f1',
	'inp_material-c1p5_f0p8',
	'inp_material-c1p75_f0p8',
	'inp_material-c2_f0p8',
	'inp_material-c4_f0p8',
	'inp_material-c7_f0p8',
    ]
for file_name in list_of_models:

	# this is the setup  for where the files are

	input_name = file_name
	output_name = file_name+"_MaterialEdited"

	current_dir = "D:/COFO - HP/01 PhD research/202403 - Bern skull/WP5 - bern-001/03 - Simulation Setup/034 - material edit"
	parent_dir = os.path.dirname(current_dir)
	os.chdir(current_dir)
	print(f"working in directory: {current_dir}")

	mdb.ModelFromInputFile(name=input_name, 
	    inputFileName=parent_dir + '/033 - apply material/inp files/' + input_name + '.inp')

	model_name = input_name
	part_name = mdb.models[model_name].parts.keys()[-1]

	#================ edit the bone density ================
	E_0 = 10000
	rho_inf = 0.45
	rho_sup = 0.85
	c_0 = 2.635
	c_1 = -14.062
	c_2 = 24.498
	c_3 = -12.265
	alpha = 0.54
	k = 1.6

	for matos in mdb.models[model_name].materials.keys() :
		density = float(str(mdb.models[model_name].materials[matos].elastic.table[0]).split(',')[0].replace('(', ''))
		if 0 <= density and density < rho_inf:
			fonc = alpha*density**k
		elif rho_inf <= density and density < rho_sup:
			fonc = c_0 + c_1*density + c_2*density**2 + c_3*density**3
		elif rho_sup <= density and density <= 1:
			fonc = density
		else:
			print(f"!!! ERROR : some density are not between 0 and 1 in material {matos} !!!")
		E = fonc * E_0
		mdb.models[model_name].materials[matos].Density(table=((density*1.8e-9, ), ))
		mdb.models[model_name].materials[matos].Elastic(table=((float(E), float(0.3)), ))
		mdb.models[model_name].materials[matos].setValues(description='material has been edited: BVTV = ' + str(density))



	#================ copy assembly level keratine set to part level ========================

	assembly_set_keratine = 'TET99'
	part_set_keratine = 'set-Horn'

	# Open the model database
	model = mdb.models[model_name]
	assembly = model.rootAssembly

	# Get the assembly set
	assemblySet = assembly.sets[assembly_set_keratine]

	# Switch to the part module
	part = model.parts[part_name]

	# Create a new set in the part module using the elements from the assembly set
	elementLabels = [element.label for element in assemblySet.elements]
	part.SetFromElementLabels(name=part_set_keratine, elementLabels=elementLabels)


	# ============= edit keratine properties =============

	mdb.models[model_name].Material(name='KERATIN')
	mdb.models[model_name].materials['KERATIN'].Density(table=((float(float(1.3e-09)), ), ))
	mdb.models[model_name].materials['KERATIN'].Elastic(table=((float(2e3), float(0.3)), ))
	mdb.models[model_name].materials['KERATIN'].Damping(alpha=float(0.1))
	mdb.models[model_name].HomogeneousSolidSection(material='KERATIN', name='Section-KERATIN', thickness=None)

	mdb.models[model_name].parts['PART-1'].SectionAssignment(
	    offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, 
	    region=mdb.models[model_name].parts['PART-1'].sets['set-Horn'], 
	    sectionName='Section-KERATIN', 
	    thicknessAssignment=FROM_SECTION)

	# ============= save results =============

	mdb.Job(activateLoadBalancing=False, atTime=None, contactPrint=OFF, 
	    description='', echoPrint=OFF, explicitPrecision=DOUBLE, historyPrint=OFF, 
	    memory=90, memoryUnits=PERCENTAGE, model=model_name, modelPrint=OFF, 
	    multiprocessingMode=DEFAULT, name=output_name, nodalOutputPrecision=SINGLE, 
	    numCpus=14, numDomains=14, parallelizationMethodExplicit=DOMAIN, 
	    queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS, 
	    userSubroutine='', waitHours=0, waitMinutes=0)

	mdb.jobs[output_name].writeInput(consistencyChecking=OFF)