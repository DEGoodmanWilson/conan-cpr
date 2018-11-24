#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class CprConan(ConanFile):
    name = "cpr"
    version = "1.3.0"
    url = "https://github.com/DEGoodmanWilson/conan-cpr"
    description = "C++ Requests: Curl for People, a spiritual port of Python Requests"
    license = "https://github.com/whoshuu/cpr/blob/1.3.0/LICENSE"
    homepage = "http://whoshuu.github.io/cpr/"

    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
               "use_ssl": [True, False]}
    default_options = {"shared": False,
                       "libcurl:with_ldap": False,
                       "use_ssl": True}
    generators = "cmake"

    def requirements(self):
        self.requires("libcurl/7.56.1@bincrafters/stable")

    def configure(self):
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.version <= "12":
            raise ConanInvalidConfiguration("Visual Studio <= 12 is not supported")

        self.options["libcurl"].with_openssl = bool(self.options.use_ssl)

    def source(self):
        source_url = "https://github.com/whoshuu/cpr"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_SYSTEM_CURL"] = True # Force CPR to not try to build curl itself from a git submodule
        cmake.definitions["BUILD_CPR_TESTS"] = False
        cmake.configure()
        return cmake

    def build(self):
        if self.settings.os == "Macos" and self.options.shared:
            # TODO: Is it a bug in libcurl package?
            tools.replace_in_file(os.path.join('sources', 'cpr', 'CMakeLists.txt'),
                                  """target_link_libraries(${CPR_LIBRARIES}""",
                                  """target_link_libraries(${CPR_LIBRARIES} z""")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        with tools.chdir("sources"):
            self.copy(pattern="LICENSE")
            self.copy(pattern="*", dst="include", src="sources/include", keep_path=True)
            self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
            self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
            self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False)
            self.copy(pattern="*.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['cpr',]
        if self.settings.os != "Windows":
            self.cpp_info.cppflags = ["-pthread"]
        