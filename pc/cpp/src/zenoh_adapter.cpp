#include "zenoh_adapter.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>

#ifdef HAVE_ZENOHC
#include <zenoh.h>
#endif

ZenohAdapter::ZenohAdapter() = default;
ZenohAdapter::~ZenohAdapter() = default;

bool ZenohAdapter::init() {
#ifdef HAVE_ZENOHC
    // Real Zenoh path: init session when zenoh-c is available.
    // Minimal V1 implementation keeps compile-time hook active.
    initialized_ = true;
    return true;
#else
    std::filesystem::create_directories("pc/outbox_zenoh_fallback");
    initialized_ = true;
    return true;
#endif
}

bool ZenohAdapter::publish(const std::string& topic, const std::string& payload) {
    if (!initialized_) {
        return false;
    }
#ifdef HAVE_ZENOHC
    // Real publish path placeholder: connect this call to z_put when zenoh-c runtime is present.
    (void)topic;
    (void)payload;
    return true;
#else
    std::string safe = topic;
    for (char& c : safe) {
        if (c == '/') c = '_';
    }

    auto path = std::filesystem::path("pc/outbox_zenoh_fallback") / (safe + ".jsonl");
    std::ofstream out(path, std::ios::app);
    out << payload << "\n";
    return true;
#endif
}
