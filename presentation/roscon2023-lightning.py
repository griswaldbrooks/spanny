#!/usr/bin/env python3
import elsie
from elsie.ext import unordered_list
from elsie.boxtree.box import Box

slides = elsie.SlideDeck(width=1920, height=1080)

slides.update_style("default", elsie.TextStyle(font="Lato", align="left", size=64))
slides.update_style("code", elsie.TextStyle(size=38))
slides.set_style("link", elsie.TextStyle(color="blue"))


def logo_header_slide(parent: Box, title: str):
    parent.sbox(name="header", x=0, height=140).fbox(p_left=20).text(
        title, elsie.TextStyle(bold=True)
    )
    return parent.fbox(name="content", p_left=20, p_right=20)


def image_slide(parent: Box, title: str, image_path: str):
    content = logo_header_slide(parent, title)
    content = content.fbox(horizontal=True, p_top=20, p_bottom=20)
    text_area = content.fbox(name="text_area", width="50%")
    content.sbox(name="image", width="fill").image(image_path)
    return text_area


def section_title_slide(parent: Box, title: str, subtitle: str):
    content = logo_header_slide(parent, "")
    content.sbox().text(title, elsie.TextStyle(align="right", size=240, bold=True))
    content.box().text(subtitle)


def code_slide(parent: Box, title: str, language: str, code: str):
    content = logo_header_slide(parent, title)
    code_bg = "#F6F8FA"
    box = content.box(y=0, width="100%", height="100%", p_bottom=20)
    box.rect(bg_color=code_bg, rx=20, ry=20)
    return box.overlay().box(x=0, y=0, p_left=20, p_right=20, p_top=20, p_bottom=20).code(
        language, code, use_styles=True
    )

def add_footer(parent: Box):
    footer = parent.box(width="fill", height="5%", horizontal=True)
    conference = footer.box(width="fill", height="fill")
    conference.text(" ROSCon 2023", elsie.TextStyle(color="grey", size=32, align="left"))
    author_repo = footer.box(width="fill", height="fill")
    author_repo.text("Griswald Brooks   |   github.com/griswaldbrooks/spanny  ", elsie.TextStyle(color="black", size=32, align="right"))


@slides.slide(debug_boxes=False)
def normal_usage(slide):
    code_slide(
        slide,
        "spanny: mdspan",
        "C++",
        """
// Allocate the map
std::array map_storage{...};
// Create a 2D view of the map
auto occupancy_map = std::mdspan(map_storage.data(), 384, 384);
// Update the map 
for (std::size_t i = 0; i != occupancy_map.extent(0); i++) {
    for (std::size_t j = 0; j != occupancy_map.extent(1); j++) {
        occupancy_map[i, j] = get_occupancy_from_laser_scan(...)
    }
}
""",
    )
    slide.overlay().box(x=1200, y=570).image("images/turtlebot3_world.jpg", scale=1.0)
    add_footer(slide)


@slides.slide(debug_boxes=False)
def policy_injection(slide):
    code_slide(
        slide,
        "spanny: policy injection",
        "C++",
        """
using bin_view = 
std::mdspan<class T, class Extents, class LayoutPolicy, class Accessor>;
""",
    )
    slide.set_style("footer", elsie.TextStyle(color="black", size=32, align="right"))
    add_footer(slide)


@slides.slide(debug_boxes=False)
def async_bin_checker(slide):
    cslide = code_slide(
        slide,
        "spanny: bin accessor",
        "C++",
        """
using bin_view = 
std::mdspan<class T, class Extents, class LayoutPolicy, ~#ACCESSOR{bin_checker}>;

struct bin_checker {
  using element_type = bin_state;
  using reference = std::future<bin_state>;
  using data_handle_type = robot_arm*;

  reference access(data_handle_type ptr, std::ptrdiff_t offset) const {
    return std::async([=]{
      return bin_state{ptr->is_bin_occupied(static_cast<int>(offset)),
                       offset_to_coord(static_cast<int>(offset))};
    });
  }
};
""",
    )
    ploc = cslide.inline_box("#ACCESSOR").p("50%", "100%")
    arrow = elsie.Arrow(20)
    slide.line([ploc.add(0, -50), ploc.add(0, -100)], stroke_width=10, start_arrow=arrow, color="orange")
    slide.set_style("footer", elsie.TextStyle(color="black", size=32, align="right"))
    add_footer(slide)

@slides.slide(debug_boxes=False)
def bounds_checker(slide):
    cslide = code_slide(
        slide,
        "spanny: bin layout",
        "C++",
        """
using bin_view = 
std::mdspan<class T, class Extents, ~#LAYOUT{bin_layout}, bin_checker>;

struct bin_layout {
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
""",
    )
    ploc = cslide.inline_box("#LAYOUT").p("50%", "100%")
    arrow = elsie.Arrow(20)
    slide.line([ploc.add(0, -50), ploc.add(0, -100)], stroke_width=10, start_arrow=arrow, color="orange")
    slide.set_style("footer", elsie.TextStyle(color="black", size=32, align="right"))
    add_footer(slide)


@slides.slide(debug_boxes=False)
def async_implementation(slide):
    code_slide(
        slide,
        "spanny: beer view",
        "C++",
        """
using bin_view = 
std::mdspan<bin_state, six_pack, bin_layout, bin_checker>;

auto arm = robot_arm{"/dev/ttyACM0", 9600};
auto bins = bin_view(&arm);
while(true) {
  std::vector<std::future<bin_state>> futures;
  for (auto i = 0u; i < bins.extent(0); ++i) 
    for (auto j = 0u; j < bins.extent(1); ++j) 
        futures.push_back(bins(i, j));
    
  for (auto const& future : futures) future.wait();
    
  for (auto& future : futures) print_state(future.get());
    
  std::cout << "====================" << std::endl;
}
""",
    )
    slide.set_style("footer", elsie.TextStyle(color="black", size=32, align="right"))
    add_footer(slide)


@slides.slide(debug_boxes=False)
def demo_time(slide):
    content = logo_header_slide(slide, "")
    content.box(width="fill").text(
        "Demo Time", elsie.TextStyle(size=160, bold=True)
    )
    
    slide.set_style("footer", elsie.TextStyle(color="black", size=32, align="right"))
    add_footer(slide)
    
@slides.slide(debug_boxes=False)
def thank_you(slide):
    logo_header_slide(slide, "Thanks")
    slide.overlay().image("roscon2023/qr.png", scale=2.0)
    add_footer(slide)


slides.render("roscon2023-lightning.pdf")
