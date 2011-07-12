#include <list>
#include <string>
#include <iostream>

#if defined (_WIN32)
  #if defined (ExampleLib_EXPORTS)
      #define EXPORT __declspec(dllexport)
  #else
      #define EXPORT __declspec(dllimport)
  #endif
#else
      #define EXPORT 
#endif


class Item 
{
    private:
        std::string d;
    public:

	EXPORT Item(const Item &o);
        EXPORT std::string getD() const;
        EXPORT Item(std::string d_);
        EXPORT Item& operator=(const Item &other);
};


class Container
{
    private:
        std::list<Item> items;

    public:
        EXPORT Container() {
            items = std::list<Item>();
        }

        EXPORT const std::list<Item>& getItems() const;
        EXPORT const Item& getFront() const;
        EXPORT const Item& getBack() const;
        EXPORT void  addItem(Item &it);
	EXPORT int   size() const;
};


class Filler
{
    public:
        EXPORT static void filler(int anzahl, Container& cont);
        EXPORT static void throwException() ;
};




