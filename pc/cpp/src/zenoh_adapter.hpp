#pragma once

#include <string>

class ZenohAdapter {
public:
    ZenohAdapter();
    ~ZenohAdapter();

    bool init();
    bool publish(const std::string& topic, const std::string& payload);

private:
    bool initialized_{false};
};
