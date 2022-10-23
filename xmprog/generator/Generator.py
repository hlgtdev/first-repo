from CodeGenerator import *
from ClassGenerator import *
from PlantumlGenerator import *

class Generator():

	forceDryRun = False

	@classmethod
	def generate(cls, example, dryRun=False, pumlReplacements={}):

		dryRun = dryRun or cls.forceDryRun

		ClassGenerator.generate(example)
		PlantumlGenerator.generate(example, dryRun=dryRun, pumlReplacements=pumlReplacements)
		CodeGenerator.generate(example)
