import csv

from pymongo import MongoClient
from bson import ObjectId
from utils import Utils

csv_filename = 'kdi-local-elections-observations-first-round-2013.csv'

# Connect to default local instance of mongo
client = MongoClient()

# Get database and collection
db = client.kdi
collection = db.localelectionsfirstround2013

# Clear data
collection.remove({})

def parse_csv():
	'''
	Reads the KDI local election monitoring CSV file.
	Creates Mongo document for each observation entry.
	Stores generated JSON documents.
	'''
	with open(csv_filename, 'rb') as csvfile:
		reader = csv.reader(csvfile)
		# Skip the header
		next(reader, None)
		
		# Iterate through the rows, retrieve desired values.
		for row in reader:
			# POLLING STATION
			polling_station_number = row[3].lower() # Column name: nrQV
			room_number = row[4] # Column name: NRVV
			
			commune = row[5] # Column name: Komuna
			polling_station_name = row[6] # Column name: EQV
			
			# ARRIVAL TIME
			arrival_time = row[9] # column name: P01KA
			how_to_vote_info = row[10] # column name: P02A
			list_of_candidates = row[11] # column name: P02B
			when_preparation_start = row[12] # column name:P03Perg
			number_KVV_members = row[13] #column name:P04KVV
			female = row[14] #column name:P04Fem
			UV_lamp = row[15] #column name:P05Lla
			spray = row[16] # column name:P05Ngj
			voters_list = row[17] # column name:P05Lis
			ballots = row[18] # column name:P05Flv	
			stamp = row[19] # column name:P05Vul
			ballot_box = row[20] # column name:P05Kut
			voters_book = row[21] # column name:P05Lib
			voting_cabin = row[22] # column name:P05Kab
			envelops_condition_voters = row[23] # column name:P05ZFK
			number_of_accepted_ballots = row[24] # column name:P06NFP
			number_of_voters_in_voting_station_list = row[25] # column name: P07VNL
			number_of_voting_cabins=row[26] # column name:P08NKV
			votingbox_shown_empty=row[27] # column name:P09TKZ
			closed_with_safetystrip = row[28] # column name:P10SHS
			did_they_register_serial_number_of_strips = row[29] # column name:P11NRS
			cabins_provided_voters_safety_and_privancy = row[30] # column name:P12KFV

	

			# VOTING MATERIAL
			material_left_behind = row[7] # Column name: 01gja
			have_physical_access = row[8] # Column name: 02gja
			
			# VOTER INFORMATION
			ultra_violet_control = row[45] # Column name: PV03UVL
			identified_with_document = row[46] # Column name: PV04IDK
			finger_sprayed = row[47] # Column name: PV05GSH
			sealed_ballot = row[48] # Column name: PV06VUL
			
			how_many_voted_by_ten_AM = row[49] # Column name: PV07-10
			how_many_voted_by_one_PM = row[50] # Column name: PV07-13
			how_many_voted_by_four_PM = row[51] # Column name: PV07-16
			how_many_voted_by_seven_PM = row[52] # Column name: PV07-19
			
			# IRREGULARITY AND COMPLAINTS
			attempt_to_vote_moreThanOnce=row[60] #Column name: PA01x1
			allowed_to_vote=row[61] #Column name: PA01ifPO
			take_picture_ofballot=row[62] #Column name: PA02Fot
			inserted_more_than_one_ballot_in_the_box=row[63] #Column name: PA03M1F
			unauthorized_persons_stayed_at_the_voting_station=row[64] #Column name: PA04PPD
			violence_in_the_voting_station=row[65] #Column name: PA05DHU
			politic_propaganda_inside_the_voting_station=row[66] #Column name: PA06PRP
			more_than_one_person_behind_the_cabin=row[67] #Column name: PA07M1P
			has_the_voting_station_been_closed_in_any_case=row[68] #Column name: PA08MBV
			case_voting_outside_the_cabin=row[69] #Column name: PA09VJK
			how_many_voters_complained_during_the_process=row[70] #Column name: PA10VAV
			how_many_voters_filled_the_complaints_form=row[71] #Column name: PA11VMF
			any_accident_happened_during_the_process=row[72] #Column name: PA12PAA	
			
			# BALLOTS - MUNICIPAL ASSEMBLY ELECTIONS
			total_ballots_mae = row[101] # PAK01
			invalid_ballots_in_box_mae = row[102] # PAK02
			ballots_set_aside_mae = row[103] # PAK03
			# something = row[104] # PAK04
				
			# BALLOTS - MAYOR ELECTIONS
			total_ballots_me = row[105] # PKK01
			invalid_ballots_in_box_me = row[106] # PKK02
			ballots_set_aside_me = row[107] # PKK03
			bollots_put_in_transaparent_bag = row[108] # PKK04
			
			# TODO: Figure out if invalid_ballots_in_box_xxx and ballots_set_aside_xxx are redundant.
			# If invalid_ballots_in_box_xxx and ballots_set_aside_xxx refer to the same thing then we only need to count (invalid_ballots_in_box_xxx) and not the flag (ballots_set_aside_xxx)
			
			#FIXME: When dealing with numbers, set in document as int instead of string.
			#FIXME: Translate PO/YO to True/False boolean values.
			#FIXME: Translate mutlti-choice values to english (e.g. Gjithmone to Always)
			util = Utils()
			observation = {
				'_id': str(ObjectId()),
				'pollingStation':{
					'number': polling_station_number,
					'roomNumber': room_number,
					'name': polling_station_name,
					'commune': commune
				},
				'onArrival':{
					'materialLeftBehind': util.to_boolean(material_left_behind),
					'havePhysicalAccess': util.to_boolean(have_physical_access)
				},
				'preparation':{
					'arrivalTime': arrival_time,
					'votingMaterialsPlacedInAndOutVotingStation':{
						'howToVoteInfo': util.to_boolean(how_to_vote_info),
						'listOfCandidates': util.to_boolean(list_of_candidates), 
						'whenPreparationStarted': when_preparation_start,
						'kvvMembers':{
							'total': util.to_num(number_KVV_members), 
							'female': util.to_num(female) 
						}
					},
				'missingMaterial':{
					'uvLamp': util.to_boolean(UV_lamp), 
					'spray':util.to_boolean( spray), 
					'votersList': util.to_boolean(voters_list),
					'ballots': util.to_boolean(ballots),	
					'stamp': util.to_boolean(stamp),
					'ballotBox':util.to_boolean(ballot_box),
					'votersBook': util.to_boolean(voters_book),
					'votingCabin': util.to_boolean(voting_cabin), 
					'envelopsForConditionVoters': util.to_boolean(envelops_condition_voters),
				},
				'numberOfAcceptedBallots': util.to_num(number_of_accepted_ballots), 
				'numberOfVotersInVotingStationList':util.to_num(number_of_voters_in_voting_station_list),
				'numberOfVotingCabins':util.to_num(number_of_voting_cabins),
				'votingBoxShownAsEmpty': util.to_boolean(votingbox_shown_empty),
				'closedWithSafetyStrip':util.to_boolean( closed_with_safetystrip), 
				'registeredStrips': util.to_boolean(did_they_register_serial_number_of_strips), 
				'cabinsSafetyAndPrivacy': util.to_boolean(cabins_provided_voters_safety_and_privancy),
				},
				'votingProcess':{
					'voters':{
						'ultraVioletControl': util.translate_frequency(ultra_violet_control),
						'identifiedWithDocument': util.translate_frequency(identified_with_document),
						'fingerSprayed': util.translate_frequency(finger_sprayed),
						'sealedBallot': util.to_num(sealed_ballot),
						'howManyVotedBy':{
							'tenAM': util.to_num(how_many_voted_by_ten_AM),
							'onePM': util.to_num(how_many_voted_by_one_PM),
							'fourPM': util.to_num(how_many_voted_by_four_PM),
							'sevenPM': util.to_num(how_many_voted_by_seven_PM)
						}
					}
				},
				'irregularities':{
					'attemptToVoteMoreThanOnce':util.to_boolean(attempt_to_vote_moreThanOnce),
					'allowedToVote':util.to_boolean(allowed_to_vote),
					'photographedBallot':util.to_boolean(take_picture_ofballot),
					'insertedMoreThanOneBallot':util.to_boolean(inserted_more_than_one_ballot_in_the_box),
				 	'unauthorizedPersonsStayedAtTheVotingStation':util.to_boolean(unauthorized_persons_stayed_at_the_voting_station),
					'violenceInTheVotingStation':util.to_boolean(violence_in_the_voting_station),
					'politicalPropagandaInsideTheVotingStation':util.to_boolean(politic_propaganda_inside_the_voting_station),
					'moreThanOnePersonBehindTheCabin':util.to_boolean(more_than_one_person_behind_the_cabin),
					'hasTheVotingStationBeenClosedInAnyCase':util.to_boolean(has_the_voting_station_been_closed_in_any_case),
					'caseVotingOutsideTheCabin':util.to_num(case_voting_outside_the_cabin),
					'anyAccidentHappenedDuringTheProcess':util.to_boolean(any_accident_happened_during_the_process)
				},					
				'complaints':{
					'total':util.to_num(how_many_voters_complained_during_the_process),
					'filed':how_many_voters_filled_the_complaints_form	#FIXME: This is meant to be a number but instead it's a frequency term.
				},
				'ballots':{
					'municipalAssembly':{
						'total': util.to_num(total_ballots_mae),
						'invalid':{
							'inBallotBox': util.to_num(invalid_ballots_in_box_mae),
							'setAside': util.to_boolean(ballots_set_aside_mae)
						}
					},
					'mayoral':{
						'total': util.to_num(total_ballots_me),
						'invalid':{
							'inBallotBox': util.to_num(invalid_ballots_in_box_me),
							'setAside': util.to_boolean(ballots_set_aside_me)
						},
						'putInTransparentBag': util.to_boolean(bollots_put_in_transaparent_bag)
					}
				}
			} 
			
			# Insert document
			collection.insert(observation)

parse_csv()	
