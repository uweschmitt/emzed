#include <iostream>
#include "../example.h"


int main()
{
	Container cont = Container();

	std::string *name = new std::string("test");

	Item it = Item(*name);
	cont.addItem(it);
	std::cout << "num items = " << cont.size() << std::endl;
	
	std::cout << "front = " << cont.getFront().getD() << std::endl;
	std::cout << "back  = " << cont.getBack().getD() << std::endl;

	Filler::filler(10, cont);

	std::cout << "num items = " << cont.size() << std::endl;
	std::cout << "front = " << cont.getFront().getD() << std::endl;
	std::cout << "back  = " << cont.getBack().getD() << std::endl;

	try {
		Filler::throwException();
	}
	catch (int &what)
        {
		std::cout << "caught " << what << std::endl;
        }

}
