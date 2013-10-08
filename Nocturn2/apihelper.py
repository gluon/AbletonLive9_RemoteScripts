
def print_api(object, object_name, path):
	inf = info(object)
	if (inf != ""):
		file = open(path+object_name+".txt", 'w')
		print type(object)
		file.write(inf)
		file.close()
		for oname in dir(object):
			if (oname.find("__") < 0):
				o = getattr(object, oname)
				c = 0
				if ("ABCDEFGHIJKLMNOPQRSTVWXYZ".find(oname[0]) < 0):
					c += 1
				else:
					for ooname in dir(o):
						if (ooname == "__call__"):
							c += 1
						if (ooname == object_name):
							c += 1
				if (c == 0):
					print_api(o, oname, path+object_name+".")

def info(object, spacing = 30, collapse = 1, built_in = False):
	processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
	methods = "";
	properties = "";
	for oname in dir(object):
		if ((built_in) or (oname.find("__") < 0)):
			o = getattr(object, oname)
			line = "\n"+oname.ljust(spacing)+" "+processFunc(str(o.__doc__))
			if (callable(o)):
				methods += line
			else:
				properties += line
	text = ""
	if (methods):
		text += methods+"\n"
	if (properties):
		text += properties+"\n"
	return text

def info2(object, spacing=10, collapse=1):
	"""Print methods and doc strings.

	Takes module, class, list, dictionary, or string."""
	methodList = [e for e in dir(object) if callable(getattr(object, e))]
	processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
	methods = ("\n".join(["%s %s" %
					 (method.ljust(spacing),
					  processFunc(str(getattr(object, method).__doc__)))
					 for method in methodList]))

	attribList = [e for e in dir(object) if (not callable(getattr(object, e)))]
	processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)
	attribs = ("\n".join(["%s %s" %
					 (attrib.ljust(spacing),
					  processFunc(str(getattr(object, attrib).__doc__)))
					 for attrib in attribList]))
	return methods+"\n\n"+attribs+"\n\n"

#if __name__ == "__main__":
#	print help.__doc__
