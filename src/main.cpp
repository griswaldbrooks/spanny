#include <iostream>
#include <future>
#include <memory>
#include <stdexcept>
#include <string>
#include "serial/serial.h"
#include "mdspan.hpp"

namespace stdex = std::experimental;

enum struct bin_state {
  OCCUPIED,
  EMPTY
};

struct robot_arm {
  robot_arm(
    std::string port,
    uint32_t baudrate,
    serial::Timeout timeout = serial::Timeout::simpleTimeout(10000))
    : serial_(std::move(port), baudrate, std::move(timeout)) {}

  bin_state is_bin_occupied(int bin) {
    if (!serial_.isOpen()) {
      throw std::runtime_error("Error opening serial port");
    }
    serial_.write(std::to_string(bin));
    auto const result = std::stoi(serial_.readline());
    if (result == 1) {
      return bin_state::OCCUPIED;
    } 
    return bin_state::EMPTY;
  }
  
  serial::Serial serial_;
};

struct bounds_checked_layout_policy {
  template <class Extents>
  struct mapping : stdex::layout_right::mapping<Extents> {
    using base_t = stdex::layout_right::mapping<Extents>;
    using base_t::base_t;
    std::ptrdiff_t operator()(auto... idxs) const {
      [&]<size_t... Is>(std::index_sequence<Is...>) {
        if (((idxs < 0 || idxs > this->extents().extent(Is)) || ...)) {
          throw std::out_of_range("Invalid bin index");
        }
      }(std::make_index_sequence<sizeof...(idxs)>{});
      return this->base_t::operator()(idxs...);
    }
  };
};

struct robot_command_accessor {
  using element_type = bin_state;
  using reference = std::future<bin_state>;
  using data_handle_type = robot_arm*;

  reference access(data_handle_type ptr, std::ptrdiff_t offset) const {
    // We know ptr will be valid asynchronously because we construct it on the stack
    // of main. In real code we might want to use a shared_ptr or something
    return std::async([=]{
      return ptr->is_bin_occupied(static_cast<int>(offset));
    });
  }
};

using bin_view = stdex::mdspan<bin_state, 
  // We're treating our 6 bins as a 3x2 matrix
  stdex::extents<uint32_t, 3, 2>,
  // Our layout should do bounds-checking
  bounds_checked_layout_policy,
  // Our accessor should tell the robot to asynchronously access the bin
  robot_command_accessor
>;

int main() {
  auto arm = robot_arm{"/dev/ttyACM0", 9600};
  auto bins = bin_view(&arm);
  while(true) {
    for (auto i = 0u; i < bins.extent(0); ++i) {
      for (auto j = 0u; j < bins.extent(1); ++j) {
        std::cout << "Bin " << i << ", " << j << " is ";
        try {
          auto state = bins(i, j).get();
          switch (state) {
            case bin_state::OCCUPIED:
              std::cout << "OCCUPIED";
              break;
            case bin_state::EMPTY:
              std::cout << "EMPTY";
              break;
          }
        } catch (std::exception const& e) {
          std::cout << "¯\\_(ツ)_/¯ " << e.what();
        }
        std::cout << "\n";
      }
    }
    std::cout << "====================\n";
  }
  return 0;
}