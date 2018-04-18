from struct import pack
def delimitedStream(chunk):
	_length,_lengthIndex,_temp=0,0,b''
	_readingLength=True
	while (len(chunk)):
		if _readingLength:
			b=chunk[0]
			_length+=(b & 0x7f) << (7 * _lengthIndex)
			if (b & (1<<7)):
				_lengthIndex += 1
				_readingLength = True
			else:
				_lengthIndex=0
				_readingLength=False
			chunk=chunk[1:]
		else:
			if _length<=len(chunk):
				_temp+=chunk[:_length]
				chunk=chunk[_length:]
				_length=0
				_readingLength = True
			else:
				break
	return _temp

def delimitingStream(chunk):
	_length=len(chunk)
	_temp=b''
	_b=[]
	while (_length > 0x7f):
		_b.append((1<<7)+(_length & 0x7f))
		_length>>=7
	_b.append(_length)
	_temp+=pack('<%sB'%len(_b),*_b)
	_temp+=chunk
	return _temp

if __name__=='__main__':
	# test
	bbb=b"\xc1\x01\x10\x12\x1a\xbc\x01\x08\x00\x125\n\t\xe6\xb5\x8f\xe8\xa7\x88\xe5\x99\xa8\x12$com.android.browser/.BrowserActivity\x18\x00 \x01\x12;\n\x0c\xe6\x89\x8b\xe6\x9c\xba\xe7\x99\xbe\xe5\xba\xa6\x12'com.baidu.searchbox/.BoxBrowserActivity\x18\x00 \x00\x12D\n\x0c\xe6\x89\x8b\xe6\x9c\xba\xe6\xb7\x98\xe5\xae\x9d\x120com.taobao.taobao/com.taobao.tao.BrowserActivity\x18\x00 \x00"
	sss=delimitedStream(bbb)
	print (sss)

