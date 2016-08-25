import optparse 

def parse_description_file(filename):
	try:
		f = open(filename, "r")
	except:
		print "[*] Error while opening file: " + filename
	lines = f.readlines()
	results = []
	try:
		for line in lines:
			results.append(line.strip().split("\t"))
	except:
		print "[*] Error while parsing descriptions file: " + filename
	f.close()
	return results

def parse_apdu_command(line, command_descriptions):
	command_bytes = line.strip().split(" ")
	command_bytes_len = len(command_bytes)
	cla = command_bytes[0]
	ins = command_bytes[1]
	p1 = command_bytes[2]
	p2 = command_bytes[3]
	
	if command_bytes_len == 5:
		le = command_bytes[4]
	elif command_bytes_len > 5:
		lc = int("0x" + command_bytes[5],0)
		if command_bytes_len > 5 + lc:
			le = int("0x" + command_bytes[5+lc], 0)   
			
	for cd in command_descriptions:
		if ins == cd[2]: # INS
			return ins + " : " + cd[0] + " (" + cd[1] + ")" # INS : NAME (DESC) 
	return ins + " :  (NOT FOUND)" # INS : (NOT FOUND)
	# TO-DO:
	#	- PARSE COMMANDS DEPENDING ON CLA, P1 AND P2 VALUES 

def parse_apdu_response(line, response_descriptions, last_apdu_command=None):
	response_bytes = line.strip().split(" ")
	sw1 = response_bytes[-2]
	sw2 = response_bytes[-1]
		
	for rd in response_descriptions:
		if sw1 == rd[0] and sw2 == rd[1]: # SW1, SW2
			return sw1 + "" + sw2 + " : " + rd[3] + " [" + rd[2] + "]" # SW1SW2 : NAME [TYPE]
	return sw1 + "" + sw2 + " : (NOT FOUND)" # SW1SW2 : (NOT FOUND)
	# TO-DO: 
	# 	- RECOGNIZE SWs THAT INCLUDE XX VALUES
	#   - PARSE CUSTOM RESPONSE CODES DEPENDING ON LAST APDU COMMAND

def main():
	parser = optparse.OptionParser('usage %prog -i <input_file>')
	parser.add_option('-i','--input', dest='input_file', type='string', help='specify input file')
	parser.add_option('-o','--output', dest='output_file', type='string', help='specify output file')
	
	parser.add_option('-c', '--commands', action='store_true', dest='just_commands', default=False, help='specify if input file just contains APDU commands')
	parser.add_option('-r', '--responses', action='store_true', dest='just_responses', default=False, help='specify if input file just contains APDU responses')
	
	parser.add_option('-C', '--command-descriptions', dest='command_descriptions', type='string', help='specify custom command descriptions file')
	parser.add_option('-R', '--response-descriptions', dest='response_descriptions', type='string', help='specify custom response descriptions file')

	(options, args) = parser.parse_args()
	
	input_file = None
	output_file = None	
	last_apdu_command = None
	
	just_commands = options.just_commands
	just_responses = options.just_responses
	
	command_descriptions = None
	response_descriptions = None
	
	# input file
	if options.input_file == None:
		print parser.usage
		print 
		exit(0)
	else:
		input_file = open(options.input_file,"r")
		apdu_lines = input_file.readlines()
		input_file.close()
	
	# output file 
	if options.output_file != None:
		output_file = open(options.output_file,"w")

	if just_commands and options.just_responses:
		print parser.usage
		print "[*] Error: --commands and --responses options cannot be set at the same time"
		exit(0)

	# custom command descriptions
	if not just_responses:
		if options.command_descriptions != None:
			command_descriptions = parse_description_file(options.command_descriptions)
		else:
			command_descriptions = parse_description_file("command_descriptions.txt")
	
	# custom response descriptions
	if not just_commands:
		if options.response_descriptions != None:
			response_descriptions = parse_description_file(options.response_descriptions)
		else:
			response_descriptions = parse_description_file("response_descriptions.txt")
		
	# parse adpu lines
	is_next_command = True # this var is used to iterate between commands and responses 
	for apdu_line in apdu_lines:
		apdu_line = apdu_line.strip()
		# apdu command
		if just_commands:
			result = parse_apdu_command(apdu_line, command_descriptions)
		# apdu response
		elif just_responses:			
			result = parse_apdu_response(apdu_line, response_descriptions, last_apdu_command)
		# apdu commands and responses
		else:
			if is_next_command:
				result = parse_apdu_command(apdu_line, command_descriptions)
				last_apdu_command = apdu_line
				is_next_command = False
			else:
				result = parse_apdu_response(apdu_line, response_descriptions, last_apdu_command)
				last_apdu_command = None
				is_next_command = True 
		# show parsed results
		print result
		print "\t" + apdu_line
		if output_file != None:
			output_file.write(result + "\n")
			output_file.write("\t" + apdu_line + "\n")
	
	# close output files
	if output_file != None:
		output_file.close()

if __name__ == '__main__':
	main()