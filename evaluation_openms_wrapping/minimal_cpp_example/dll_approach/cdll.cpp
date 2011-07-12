#include "../example.h"
#include <string>
#include <iostream>

#if defined EXPORT
	#undef EXPORT
#endif

#if defined (_WIN32)
  #if defined (cdll_EXPORTS)
      #define EXPORT __declspec(dllexport)
  #else
      #define EXPORT __declspec(dllimport)
  #endif
#else
      #define EXPORT 
#endif

std::exception ee;

#define BEGIN try {
#define END   } catch (std::exception e) { ee=e; }

extern "C" EXPORT void* buildContainer()
{
	return (void*) new Container();
}

extern "C" EXPORT void freeContainer(void *w)
{
	delete ((Container *) w);
}

extern "C" EXPORT void* buildString(char *name)
{
	return (void*) new std::string(name);
}

extern "C" EXPORT void freeString(void *w)
{
	delete (std::string *) w;
}

extern "C" EXPORT void* buildItem(void *name)
{
	std::string* s = (std::string *)name;
	return (void*) new Item(*s);
}

extern "C" EXPORT void  freeItem(void *item)
{
	delete (Item *) item;
}

char* stringToCharArray(std::string s)
{
	char* buff = new char[s.size()+1];
	//std::cout << "char buff at " << (void *) buff << " constructed " << std::endl;
	strcpy(buff, s.c_str());
	return buff;
}

extern "C" EXPORT void freeCharArray(char *buff)
{
	//std::cout << "free char buff at " << (void *) buff << std::endl;
	delete[] buff;
}

extern "C" EXPORT const char* getD(void *p)
{
	Item *it = (Item *)p;
	return stringToCharArray(it->getD());
}

extern "C" EXPORT void containerAddItem(void *p1, void *p2)
{
	Container *c = (Container *) p1;
	Item * it    = (Item *) p2;
	c->addItem(*it);
}

extern "C" EXPORT void* containerGetFront(void *p)
{
	Container *cont = (Container *)p;
	Item it = cont->getFront();
        Item *rv = new Item(it);
	return (void *) rv;
}

extern "C" EXPORT void* containerGetBack(void *p)
{
	Container *cont = (Container *)p;
	Item it = cont->getBack();
        Item *rv = new Item(it);
	return (void *) rv;
}

extern "C" EXPORT void FillerFiller(int n, void *p)
{
	Container* cont = (Container *)p;
	Filler::filler(n, *cont);
}

extern "C" EXPORT int containerSize(void *p)
{
	return ((Container *)p)->size();
}

extern "C" EXPORT void throwException()
{
	BEGIN
	Filler::throwException();
	END
}

extern "C" EXPORT void* getException()
{
	return &ee;
}
