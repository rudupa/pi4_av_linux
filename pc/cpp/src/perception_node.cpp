#include <chrono>
#include <deque>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "zenoh_adapter.hpp"

using Clock = std::chrono::steady_clock;

struct Frame {
    int id;
    std::string ts;
};

struct Metrics {
    uint64_t received = 0;
    uint64_t processed = 0;
    uint64_t dropped = 0;
    double fps = 0.0;
    double infer_ms = 0.0;
};

static std::string utc_now() {
    auto now = std::chrono::system_clock::now();
    std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm = *std::gmtime(&t);
    std::ostringstream os;
    os << std::put_time(&tm, "%Y-%m-%dT%H:%M:%SZ");
    return os.str();
}

int main() {
    constexpr double target_hz = 33.0;
    constexpr auto period = std::chrono::milliseconds(30);

    std::filesystem::create_directories("pc/outbox_cpp");

    std::deque<Frame> q;
    const size_t qmax = 2;
    Metrics m;
    int seq = 0;

    auto next_tick = Clock::now();
    auto t0 = Clock::now();

    std::mt19937 rng{42};
    std::uniform_int_distribution<int> obj_count(0, 8);
    std::uniform_real_distribution<double> conf(0.4, 0.95);

    ZenohAdapter zenoh;
    zenoh.init();

    while (seq < 300) {
        next_tick += period;

        Frame f{seq, utc_now()};
        m.received++;
        if (q.size() >= qmax) {
            q.pop_front();
            m.dropped++;
        }
        q.push_back(f);

        if (!q.empty()) {
            auto start = Clock::now();
            Frame cur = q.back();
            q.clear();

            int n = obj_count(rng);
            std::ostringstream payload;
            payload << "{\n";
            payload << "  \"schema_version\": 1,\n";
            payload << "  \"timestamp_utc\": \"" << cur.ts << "\",\n";
            payload << "  \"source\": \"pc-perception-cpp\",\n";
            payload << "  \"sequence_id\": " << cur.id << ",\n";
            payload << "  \"objects\": [\n";
            for (int i = 0; i < n; ++i) {
                payload << "    {\"id\":\"cam-" << i << "\",\"class\":\"vehicle\",\"confidence\":"
                        << std::fixed << std::setprecision(3) << conf(rng)
                        << ",\"bbox\":[10,10,50,50],\"range_m\":12.0,\"rel_velocity_mps\":0.2,\"source_flags\":[\"camera\",\"radar\",\"fused\"],\"track_state\":\"tracked\"}"
                        << (i + 1 == n ? "\n" : ",\n");
            }
            payload << "  ]\n";
            payload << "}\n";

            auto out = std::filesystem::path("pc/outbox_cpp") / (std::to_string(cur.id) + "_perception_objects.json");
            std::ofstream(out) << payload.str();
            zenoh.publish("/av/perception/objects", payload.str());

            auto dt = std::chrono::duration<double, std::milli>(Clock::now() - start).count();
            m.infer_ms = dt;
            m.processed++;
        }

        auto elapsed = std::chrono::duration<double>(Clock::now() - t0).count();
        m.fps = (elapsed > 0.0) ? (static_cast<double>(m.processed) / elapsed) : 0.0;

        if (seq % 33 == 0) {
            std::cout << "{\"received\":" << m.received << ",\"processed\":" << m.processed
                      << ",\"dropped\":" << m.dropped << ",\"fps\":" << std::fixed << std::setprecision(2) << m.fps
                      << ",\"infer_ms\":" << std::fixed << std::setprecision(2) << m.infer_ms << "}\n";
        }

        std::this_thread::sleep_until(next_tick);
        ++seq;
    }

    return 0;
}
