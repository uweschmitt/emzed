#include <iostream>
#include <sstream>
#include "example.h"



std::string Item::getD()  const
{
    return d;
}

void Item::setD(std::string d)
{
    this->d = d; 
}

Item::Item() { }

Item::Item (std::string d) 
{
        this->d = d;
           
}


Item::Item (const Item &o)
{
    if (this == &o) return;
    d = o.d;
}

Item& Item::operator=(const Item &other)
{
    d = other.d;
    return *this;
}


const std::list<Item>& Container::getItems() const
{
    return items;
}

int Container::size() const
{
	return items.size();
}


const Item& Container::getFront()  const
{
    return items.front();
}

const Item& Container::getBack()  const
{
    return items.back();
}

void Container::addItem(Item &it)
{
    items.push_back(it);
}

void Filler::filler(int anzahl, Container& cont)
{
	
    for (int i=0; i<anzahl; ++i)
	{
		std::ostringstream os;
        os << "item " << i;
		Item it(os.str());
		cont.addItem(it);
	}

}

void Filler::throwException() 
{
    throw 20;
}






