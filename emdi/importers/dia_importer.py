import abc
import csv
from bson import ObjectId
from pymongo import MongoClient
from slugify import slugify

class DiaImporter(object):
	__metaclass__ = abc.ABCMeta

	def __init__(self, csv_filepath, collection_name, utils):
		self.collection_name = collection_name
		self.csv_filepath = csv_filepath

		self.mongo = MongoClient()

		# Clear collection prior to import.
		self.mongo.kdi[collection_name].remove({})

		# FIXME: Passing utils as constructor argument because for some reason when we import it from DiaImporter2013 we get this error message:
		# 	AttributeError: 'module' object has no attribute 'to_boolean'
		#	WHY?!?!
		self.utils = utils


	def execute(self):
		'''
		Reads the DiA election monitoring CSV file.
		Creates Mongo document for each observation entry.
		Stores generated JSON documents.
		'''
		
		num_of_created_docs = 0

		with open(self.csv_filepath, 'rb') as csvfile:
			reader = csv.reader(csvfile)
			# Skip the header
			next(reader, None)

			# Iterate through the rows, retrieve desired values.
			for row in reader:

				# Build JSON objects.
				# The methods that build the data object are implemted in this class
				# The methods that build the JSON object are implmenet in the super-class

				# Build 'votingCenter' object.
				voting_center_data = self.build_voting_center_data(row)
				voting_center = self.build_voting_center_object(voting_center_data )

				# Build 'onArrival' object.
				on_arrival_data = self.build_on_arrival_data(row)
				on_arrival = self.build_on_arrival_object(on_arrival_data)

				# Build 'preparation' object.
				preparation_data = self.build_preparation_data(row)
				missing_materials_data = self.build_missing_materials_data(row)
				preparation = self.build_preparation_object(preparation_data, missing_materials_data)

				# Build 'voting.process' object.
				voting_process_data = self.build_voting_process_data(row)
				observers_data = self.build_voting_observers_data(row)
				refused_ballots_data = self.build_refused_ballots_data(row)
				voting_process = self.build_voting_process_object(
					voting_process_data,
					observers_data,
					refused_ballots_data)
				
				# Build 'voting.irregularities' object.
				irregularities_data = self.build_irregularities_data(row)
				irregularities = self.build_irregularities_object(irregularities_data)

				# Build 'voting.complaints' object.
				complaints_data = self.build_complaints_data(row)
				complaints = self.build_complaints_object(complaints_data)

				# Build 'voting.end' object.
				voting_end_data = self.build_voting_end_data(row)
				voting_end = self.build_voting_end_object(voting_end_data)

				# Build 'counting.ballots' object.
				counting_ballots_data = self.build_counting_ballots_data(row)
				counting_ballots = self.build_counting_ballots_object(counting_ballots_data)

				# Build 'counting.summary' object.
				counting_summary_data = self.build_counting_summary_data(row)
				counting_summary = self.build_counting_summary_object(counting_summary_data)

				results = self.build_results_object(row)

				# Build observation documents
				observation = {
					'_id': str(ObjectId()),
					'votingCenter': voting_center,
					'onArrival': on_arrival,
					'preparation': preparation,
					'voting': {
						'process': voting_process,
						'irregularities': irregularities,				
						'complaints': complaints,
						'concludes': voting_end
					},
					'counting':{
						'ballots': counting_ballots,
						'summary': counting_summary
					},
					'results': results
				}

				# Insert document
				self.mongo.kdi[self.collection_name].insert(observation)
				num_of_created_docs = num_of_created_docs + 1
			# End for

		return num_of_created_docs


	@abc.abstractmethod
	def build_on_arrival_data(self, row):
		return

	@abc.abstractmethod
	def build_on_arrival_data(self, row):
		return

	@abc.abstractmethod
	def build_preparation_data(self, row):
		return

	@abc.abstractmethod
	def build_missing_materials_data(self, row):
		return

	@abc.abstractmethod
	def build_voting_process_data(self, row):
		return

	@abc.abstractmethod
	def build_refused_ballots_data(self, row):
		return

	@abc.abstractmethod
	def build_voting_observers_data(self, row):
		return

	@abc.abstractmethod
	def build_irregularities_data(self, row):
		return

	@abc.abstractmethod
	def build_complaints_data(self, row):
		return

	@abc.abstractmethod
	def build_voting_end_data(self, row):
		return

	@abc.abstractmethod
	def build_counting_ballots_data(self, row):
		return

	@abc.abstractmethod
	def build_results_object(self, row):
		return


	def build_on_arrival_object(self, data):
		on_arrival = {
			'politicalPropagandaRemoved': self.utils.to_boolean(data[0]), #FIXME: Check if this is correct field for 2013
			'disabledHavePhysicalAccess': self.utils.to_boolean(data[1])
		}

		return on_arrival


	def build_voting_center_object(self, data):
		voting_center = {
			'name': data[5].strip(), # Polling Centre Name
			'slug': slugify(data[5].strip()),
			'number': data[2].upper(), # Number of Voting Centre
			'stationNumber': data[3].upper(), # Voting Station Number
			'commune':{
				'name': data[4].strip(), # Municipality
				'slug': slugify(data[4].strip())
			}
		}

		return voting_center


	def build_preparation_object(self, prep_data, missing_material_data):
		preparation = {
			'observerArrivalTime':prep_data[0],
			'materialsInsideAndOutsiteVotingStation':{
				'howToVoteInfo': self.utils.to_boolean(prep_data[1]),
				'listOfCandidates': self.utils.to_boolean(prep_data[2])
			},
			'preparationStartTime': prep_data[3],
			'pscMembers':{
				'total': self.utils.to_num(prep_data[4]),
				'women': self.utils.to_num(prep_data[5])
			},
			'missingMaterials': self.build_missing_materials_object(missing_material_data),
			'ballotsReceived': self.utils.to_num(prep_data[6]), # "Number of ballots received"
			'votersInVotersList': self.utils.to_num(prep_data[7]),  # "Number of voters in voters' list at the polling station"
			'votingBooths':{
				'total': self.utils.to_num(prep_data[8]), # "Number of voting booths"
				'placementEnsuredSecrecy': self.utils.to_boolean(prep_data[9]), # "Are the booths placed in such a way to ensure vote secrecy?"
			},
			'ballotBoxes':{
				'shownAsEmpty': self.utils.to_boolean(prep_data[10]), # "Was the empty ballot box shown as empty before voting starts?"
				'sealedWithSecuritySeals':self.utils.to_boolean(prep_data[11]), # "Were the ballot boxes sealed with security seals?"
				'sealsRecorded': self.utils.to_boolean(prep_data[12]), # "Were the serial numbers of seals recorded in the appropriate book?"
			}
		}

		return preparation


	def build_missing_materials_object(self, data):
		missing_materials = {}

		if len(data) > 0:
			missing_materials = {
				'uvLamp': self.utils.to_boolean(data[0]),
				'invisibleInk':self.utils.to_boolean(data[1]),
				'votersList': self.utils.to_boolean(data[2]),
				'ballots': self.utils.to_boolean(data[3]),
				'stamp': self.utils.to_boolean(data[4]),
				'ballotBox':self.utils.to_boolean(data[5]),
				'pollBook': self.utils.to_boolean(data[6]),
				'votingBooth': self.utils.to_boolean(data[7]),
				'envelopesForConditionalVote': self.utils.to_boolean(data[8])
			}

		return missing_materials
	

	def build_voting_process_object(self, voting_process_data, observers_data, refused_ballots_data):
		
		observers = self.build_observers_object(observers_data)
		refused_ballots = self.build_refused_ballots_object(refused_ballots_data)

		voting_process = {
			'pollingStationOpenTime' : voting_process_data[0],
			'observers': observers,
			'voters':{
				'ultraVioletControl': self.utils.translate_frequency(voting_process_data[1]),
				'identifiedWithDocument': self.utils.translate_frequency(voting_process_data[2]),
				'fingerSprayed': self.utils.translate_frequency(voting_process_data[3]),
				'sealedBallot': self.utils.translate_frequency(voting_process_data[4]),
				'howManyVotedBy':{
					'tenAM': self.utils.to_num(voting_process_data[5]),
					'onePM': self.utils.to_num(voting_process_data[6]),
					'fourPM': self.utils.to_num(voting_process_data[7]),
					'sevenPM': self.utils.to_num(voting_process_data[8])
				},
				'notInVotersList' : self.utils.to_num(voting_process_data[9]),
				'conditional' : self.utils.to_num(voting_process_data[10]),
				'assisted' : self.utils.to_num(voting_process_data[11]),
				'refusedBallots' : refused_ballots
			},
			'atLeastThreePscMembersPresentAtAllTimes' : self.utils.to_boolean(voting_process_data[12]),
			'comments': voting_process_data[13]
		}

		return voting_process


	def build_observers_object(self, data):
		# This object is an array, so just return the given data array.
		return data


	def build_refused_ballots_object(self, data):
		refused_ballots = {}

		if len(data) > 0:
			refused_ballots = {
				'refused': self.utils.to_boolean(data[0]),
				'total': self.utils.to_num(data[1])
			}

		return refused_ballots


	def build_irregularities_object(self, data):
		irregularities = {
			'anyoneTriedToVoteMoreThanOnce':{
				'attempted': self.utils.to_boolean(data[0]),
				'allowedToVote': self.utils.to_boolean(data[1])
			},
			'photographedBallot': self.utils.to_boolean(data[2]),
			'personInsertedMoreThanOneBallot': self.utils.to_boolean(data[3]),
		 	'unauthorizedPersonsStayedInPollingStation': self.utils.to_boolean(data[4]),
			'violenceOrThreats': self.utils.to_boolean(data[5]),
			'politicalPropagandaInsideThePollingStation': self.utils.to_boolean(data[6]),
			'moreThanOnePersonBehindTheBooth': self.utils.to_boolean(data[7]),
			'pollingStationClosedAtAnyPointDuringDay': self.utils.to_boolean(data[8]),
			'votingOutsideTheBooths': self.utils.to_boolean(data[9]),
			'incidents': self.utils.to_boolean(data[10])
		}

		return irregularities


	def build_complaints_object(self, data):

		complaints = {
			'total': self.utils.to_num(data[0]),
			'filled': self.utils.to_num(data[1]),
			'pscImpartiality' : self.utils.translate_frequency(data[2]),
		}

		return complaints


	def build_voting_end_object(self, data):

		voting_end = {
			'time': data[0], # "When did voting process end?"
			'votersStillInQueue':{ #FIXME: Weird Boolean
				'stillInQueue': self.utils.to_boolean(data[1]), # "Were there any people waiting in queue when voting center/station closed?"
				'allowedToVote':  self.utils.to_boolean(data[2]), # "Were they allowed to vote?"
			},
			'countingStartTime': data[3], # "When did the counting begin?"
			'unauthorizedPersons':{ 
				'presentDuringCounting': self.utils.to_boolean(data[4]), # "Were there any unauthorized persons present during counting?"
				'who': data[5], # "If yes, who"
			},
			'observersHadClearViewOfProcedure': self.utils.to_boolean(data[6]), # "Could the observer have a clear view of the procedures?"
			'securitySeals':{
				'checked': self.utils.to_boolean(data[7]), # "Were the security seals checked before opening the ballot box?"
				'intact': self.utils.to_boolean(data[8]), # "Were the security seals intact?"
				'verifiedAndRegistered': self.utils.to_boolean(data[12]) # "Were the security seals verified and registered?"
			},
			'votersListSignatures':{
				'countedAndRecorded': self.utils.to_boolean(data[9]), # "Were the signatures in the voters list counted and recorded?"
				'total':  self.utils.to_num(data[10]), # "Number of signature in the voters' list (how many persons voted)?"
			},
			'unusedBallots':{
				'countedAndRegistered': self.utils.to_boolean(data[11]) # "Were the unused ballots counted and registered?"
			},
			'votingMaterialsMovedAside': self.utils.to_boolean(data[13]) # "Were the voting materials moved aside (unused/damaged/refused ballots, stamps, voters' list, markers, pencils)?"
		}

		return voting_end


	def build_counting_ballots_object(self, data):
		counting_ballots = {}

		if len(data) > 0:
			counting_ballots = {
				'total': self.utils.to_num(data[0]), # "Total number of ballots in the ballot box"
				'invalid':{
					'total': self.utils.to_num(data[1]), # "How many invalid ballots were in the ballot box?"
					'movedAside': self.utils.to_boolean(data[2]) # "Were the invalid ballots moved aside?"
				}, 
				'inTransparentBag': self.utils.to_boolean(data[3]) # "After counting the ballots, were they placed in a transparent plastic bag?"
			}

		return counting_ballots


	def	build_counting_summary_object(self, data):
		counting_summary = {
			'justDecisionOnDubiousBallots': self.utils.translate_frequency(data[0]), # "Was the decision on dubious ballots just?"
			'disagreementsRecorded': self.utils.translate_frequency(data[1]), # "In case of disagreement, were they written in the book?"
			'countingFinishTime': data[2] , # "When did the counting finish?"
			'oppositions':{
				'fromRepresentativeOrObserver': self.utils.to_boolean(data[3]), # "Did any representative or observer oppose the results for this polling station?"
				'who': data[4] # "If yes, who"
			},
			'comments': data[5] # "Other comments: (If there is a discrepancy between the number of signatures and ballots in the box, explain why?)"
		}

		return counting_summary
