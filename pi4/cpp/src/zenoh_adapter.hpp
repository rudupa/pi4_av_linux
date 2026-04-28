#pragma once

#include <optional>
#include <string>

class ZenohAdapter {
public:
    ZenohAdapter();
    ~ZenohAdapter();

    bool init();
    bool publish(const std::string& topic, const std::string& payload);
    std::optional<std::string> try_get_latest(const std::string& topic);

private:
    bool initialized_{false};
};
