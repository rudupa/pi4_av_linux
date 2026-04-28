#include "zenoh_adapter.hpp"

#include <filesystem>
#include <fstream>
#include <optional>
#include <string>

#ifdef HAVE_ZENOHC
#include <zenoh.h>
#endif

ZenohAdapter::ZenohAdapter() = default;
ZenohAdapter::~ZenohAdapter() = default;

bool ZenohAdapter::init() {
#ifdef HAVE_ZENOHC
    initialized_ = true;
    return true;
#else
    std::filesystem::create_directories("pi4/outbox_zenoh_fallback");
    initialized_ = true;
    return true;
#endif
}

bool ZenohAdapter::publish(const std::string& topic, const std::string& payload) {
    if (!initialized_) return false;
#ifdef HAVE_ZENOHC
    (void)topic;
    (void)payload;
    return true;
#else
    std::string safe = topic;
    for (char& c : safe) {
        if (c == '/') c = '_';
    }
    auto path = std::filesystem::path("pi4/outbox_zenoh_fallback") / (safe + ".jsonl");
    std::ofstream out(path, std::ios::app);
    out << payload << "\n";
    return true;
#endif
}

std::optional<std::string> ZenohAdapter::try_get_latest(const std::string& topic) {
#ifdef HAVE_ZENOHC
    (void)topic;
    return std::nullopt;
#else
    std::string safe = topic;
    for (char& c : safe) {
        if (c == '/') c = '_';
    }
    auto path = std::filesystem::path("pc/outbox_zenoh_fallback") / (safe + ".jsonl");
    if (!std::filesystem::exists(path)) return std::nullopt;
    std::ifstream in(path);
    std::string line;
    std::string last;
    while (std::getline(in, line)) {
        if (!line.empty()) last = line;
    }
    if (last.empty()) return std::nullopt;
    return last;
#endif
}
