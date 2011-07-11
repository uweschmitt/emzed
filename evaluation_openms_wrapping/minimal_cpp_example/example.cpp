#include <list>
#include <string>
#include <iostream>

class Item 
{
    private:
        std::string d;
        int    i;
    public:


        const std::string getD() { return d; }
        const int     getI() { return i; }

        Item(std::string d, int i): d(d), i(i) { 
            std::cout << "construct Item(" << d << ", " << i << ") " << this << std::endl;
        }

        Item (const Item &o)
        {
            if (this == &o) return;
            d = o.d;
            i = o.i;

            std::cout << "copy construct Item(" << d << ", " << i << ") " << this << " from " << &o << std::endl;
        }
        ~Item()
        {
            std::cout << "destruct Item(" << d << ", " << i << ") " << this << std::endl;
        }
        Item& operator=(const Item &other)
        {
            std::cout << "operator " <<this << " = " << &other << std::endl;
            d = other.d;
            i = other.i;
            return *this;
        }



};

class Container
{
    private:
        std::list<Item> items;

    public:
        Container() {
            std::cout << "constructor Container called" << std::endl;
            items = std::list<Item>();
        }

        ~Container()
        {
            std::cout << "destructor Container called" << std::endl;
        }

        std::list<Item> getItemsCopy()
        {
            return items;
        }

        std::list<Item>& getItemsRef()
        {
            return items;
        }

        void addItemByRef(Item &it)
        {
            items.push_back(it);
        }

        void addItemByCopy(Item it)
        {
            items.push_back(it);
        }

};

class Filler
{
    public:
        static void filler(std::string source, Container& cont)
        {
            std::cout << __LINE__ << std::endl;
            Item it = Item("item0", 1);
            std::cout << __LINE__ << std::endl;
            cont.addItemByRef(it);
            std::cout << __LINE__ << std::endl;
            it = Item("item1", 2);
            std::cout << __LINE__ << std::endl;
            cont.addItemByCopy(it);
            std::cout << __LINE__ << std::endl;
            std::cout << "filler done" << std::endl;
        }

        static void throwException() throw (int)
        {
            throw 20;
        }
};

int testfun()
{
    Contaitestfun cont = Container();
    Filler::filler("test source", cont);
    std::cout << "DONE" << std::endl;
    Filler::throwException();
}




