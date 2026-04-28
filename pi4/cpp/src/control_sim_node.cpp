#include <chrono>
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>

#include "zenoh_adapter.hpp"

using Clock = std::chrono::steady_clock;

struct State {
    std::string mode = "auto";
    double speed = 0.0;
    double steering = 0.0;
    double throttle = 0.0;
    double brake = 0.0;
    double x = 0.0;
    double y = 0.0;
    double heading = 0.0;
    uint64_t seq = 0;
};

int main() {
    constexpr double hz = 20.0;
    constexpr double dt = 1.0 / hz;
    const auto period = std::chrono::milliseconds(50);

    std::filesystem::create_directories("pi4/outbox_cpp");

    State s;
    bool stale_perception = false;
    auto next = Clock::now();
    ZenohAdapter zenoh;
    zenoh.init();

    for (int i = 0; i < 400; ++i) {
        next += period;

        if (i % 80 == 0 && i > 0) {
            stale_perception = !stale_perception;
        }
        std::string mode_eff = stale_perception ? "degraded" : s.mode;

        auto latest = zenoh.try_get_latest("/av/perception/objects");
        if (latest) {
            stale_perception = false;
            mode_eff = s.mode;
        }

        double target_speed = (mode_eff == "auto") ? 6.0 : (mode_eff == "degraded" ? 2.5 : 0.0);
        double err = target_speed - s.speed;
        s.throttle = std::max(0.0, std::min(100.0, 25.0 * err));
        s.brake = std::max(0.0, std::min(100.0, -20.0 * err));

        double accel = 0.03 * s.throttle - 0.04 * s.brake;
        s.speed = std::max(0.0, s.speed + accel * dt);
        s.heading += s.steering * 0.03 * dt;
        s.x += s.speed * dt;

        std::ostringstream out;
        out << "{\"schema_version\":1,\"source\":\"pi4-control-sim-cpp\",\"sequence_id\":" << s.seq
            << ",\"mode\":\"" << mode_eff << "\",\"speed_mps\":" << std::fixed << std::setprecision(3) << s.speed
            << ",\"steering_deg\":" << s.steering << ",\"throttle_pct\":" << s.throttle
            << ",\"brake_pct\":" << s.brake << ",\"pose\":{\"x\":" << s.x << ",\"y\":" << s.y
            << ",\"heading_deg\":" << s.heading << "}}\n";

        auto p = std::filesystem::path("pi4/outbox_cpp") / (std::to_string(s.seq) + "_vehicle_state.json");
        std::ofstream(p) << out.str();
        zenoh.publish("/av/vehicle/state", out.str());

        if (s.seq % 20 == 0) {
            std::cout << "{\"seq\":" << s.seq << ",\"mode\":\"" << mode_eff << "\",\"speed\":" << s.speed << "}\n";
        }

        ++s.seq;
        std::this_thread::sleep_until(next);
    }

    return 0;
}
