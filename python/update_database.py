import csv
import numpy as np
import json
import pymongo
csv.field_size_limit(1000000000)

def updateDB(datafiles, comment, metadata):
	if len(comment) == 0:
		print('Must provide comment')
		return
		
	print('Parsing data file...')
	subj_data, column_labels = parse_human_data(datafiles, comment)
	
	if metadata != None:
		print('Decoding image URLs (this may take a moment)...')
		for subj in subj_data:
			stims = subj['ImgOrder']
			decode = []
			for stim in stims:
				if type(stim) == list:
					for s in stim:
						d = meta[meta['id'] == s.split('/')[-1].split('.')[0]]
						if len(d) >= 1:
							decode.append(list(d[0]))
							for idx, data in enumerate(decode[-1]):
								if isinstance(data, np.floating):
									decode[-1][idx] = float(data)
								elif isinstance(data, np.integer):
									decode[-1][idx] = int(data)
								else:
									pass
						else:
							pass
				elif type(stim) == str or unicode:
					d = meta[meta['id'] == stim.split('/')[-1].split('.')[0]]
					if len(d) >= 1:
						decode.append(list(d[0]))
						for idx, data in enumerate(decode[-1]):
								if isinstance(data, np.floating):
									decode[-1][idx] = float(data)
								elif isinstance(data, np.integer):
									decode[-1][idx] = int(data)
								else:
									pass
					else:
						pass
				else:
					print('Result type not recognized')
					
				subj['ImgDecode'] = decode
				subj['meta_dtype'] = str(meta[0].dtype)
			
	#open database
	print('Connecting to database...')
	conn = pymongo.Connection(port = 22334, host = 'localhost')
	db = conn.mturk_test
	col = db.col_test
	col.ensure_index([('WorkerID', pymongo.ASCENDING), ('Timestamp', pymongo.ASCENDING)], unique=True)
	
	print('Updating database...')
	col.insert(subj_data, safe = True)
	
	print('Update complete!')

def parse_human_data(datafiles, comment): 
        subj_data = []
        for filename in datafiles:
            with open(filename,'rb+') as csvfile:         
                datareader = csv.reader(csvfile,delimiter='\t')                      
                for row in datareader:
                    if len(row) > 0 and row[0] == 'hitid':
                        column_labels = row                
                    else:
                        try:
                            subj_data.append(json.loads(row[-1][1:-1]))
                        except ValueError:
                            continue
                        subj_data[-1]['HITid'] = row[0]
                        subj_data[-1]['HITTypeID'] = row[1]
                        subj_data[-1]['Title'] = row[2]
                        subj_data[-1]['Reward'] = row[5]
                        subj_data[-1]['URL'] = row[13]
                        subj_data[-1]['Duration'] = row[14]
                        subj_data[-1]['ViewHIT'] = row[17]
                        subj_data[-1]['AssignmentID'] = row[18]
                        subj_data[-1]['WorkerID'] = row[19] 
                        subj_data[-1]['Timestamp'] = row[23]
                        subj_data[-1]['Comment'] = comment
                csvfile.close()
        return subj_data, column_labels
        
