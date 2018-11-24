#include <cstdlib>
#include <iostream>

#include <cpr/cpr.h>


int main()
{
    auto response = cpr::Get(cpr::Url{"https://httpbin.org/get"});
    std::cout << response.text << std::endl;

    return EXIT_SUCCESS;
}
