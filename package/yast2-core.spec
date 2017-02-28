#
# spec file for package yast2-core
#
# Copyright (c) 2015 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# Optionally build with llvm-clang instead of gcc
# because we are interested in the warnings it gives.
%bcond_with clang

# Optionally treat C/C++ warnings as errors.
# It is off by default so that it will not block mass tests of new GCC
# but we want to enable it in a side repo
# to be able to fix newly detected problems relatively early.
%bcond_with werror

Name:           yast2-core
Version:        3.2.3
Release:        0
Url:            https://github.com/yast/yast-core

BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Source0:        %{name}-%{version}.tar.bz2

# obviously
BuildRequires:  boost-devel
%if %{with clang}
BuildRequires:  llvm-clang
%else
BuildRequires:  gcc-c++
%endif
BuildRequires:  libtool
# we have a parser
BuildRequires:  bison
BuildRequires:  flex
# incompatible change, parser.h -> parser.hh
BuildRequires:  automake >= 1.12
# needed for all yast packages
BuildRequires:  yast2-devtools >= 3.1.10
# testsuite
BuildRequires:  dejagnu

Summary:        YaST2 - Core Libraries
License:        GPL-2.0+
Group:          System/YaST
Requires:       perl = %{perl_version}

%description
This package contains the scanner, parser, and interpreter runtime
library for the YCP scripting language used in YaST2.

%package devel
Requires:       yast2-core = %version

Summary:        YaST2 - Core Libraries
Group:          Development/Libraries
Provides:       liby2util-devel = 2.16.1
Obsoletes:      liby2util-devel < 2.16.1
Requires:       glibc-devel
Requires:       libstdc++-devel

%description devel
This package contains include and documentation files for developing
applications using the YaST2 YCP interpreter.

%prep
%setup -n %{name}-%{version}

%build

%ifarch %arm
%if 0%{?qemu_user_space_build}
# disable autodoc building on qemu-arm only
sed -i SUBDIRS -e 's/autodocs//'
%endif
%endif

export SUSE_ASNEEDED=0 # disable --as-needed until this package is fixed

%if %{with werror}
export   CFLAGS="${RPM_OPT_FLAGS} -Werror"
export CXXFLAGS="${RPM_OPT_FLAGS} -Werror"
%endif

%if %{with clang}
export CC=clang CXX=clang++

# warning/error: argument unused during compilation
CFLAGS="${CFLAGS/-grecord-gcc-switches/}"
CXXFLAGS="${CXXFLAGS/-grecord-gcc-switches/}"
%endif

%yast_build

%install
%yast_install

mkdir -p "$RPM_BUILD_ROOT"%{yast_logdir}
%perl_process_packlist

%post
/sbin/ldconfig
# bnc#485992, since oS 11.2
C=blacklist
if test -f /etc/modprobe.d/$C; then
     mv -f /etc/modprobe.d/$C /etc/modprobe.d/50-$C.conf
fi

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)

%dir %{_libdir}/YaST2
%if "%_lib" == "lib64"
%dir /usr/lib/YaST2
%endif
%dir /usr/share/YaST2

%dir %attr(0700,root,root) %{yast_logdir}
%dir %{yast_ybindir}
%dir %{yast_plugindir}
%dir %{yast_scrconfdir}
%dir %{yast_execcompdir}/servers_non_y2

/usr/bin/ycpc
%{_libdir}/lib*.so.*
%{yast_ybindir}/startshell
%{yast_ybindir}/elf-arch
%{yast_plugindir}/lib*.so.*
%{yast_scrconfdir}/*.scr
%{yast_execcompdir}/servers_non_y2/ag_*
# perl part (stdio agents)
# *: regular build compresses them, debug does not
%{_mandir}/man3/ycp.3pm*
%{_mandir}/man3/YaST::SCRAgent.3pm*
%{perl_vendorlib}/ycp.pm
%dir %{perl_vendorlib}/YaST
%{perl_vendorlib}/YaST/SCRAgent.pm

%if 0%{?suse_version} == 0 || 0%{?suse_version} <= 1130
#  .packlist
%{perl_vendorarch}/auto/ycp
/var/adm/perl-modules/%name
%endif

%files devel
%defattr(-,root,root)
%{yast_ybindir}/ybcdump
%{_libdir}/lib*.so
%{_libdir}/lib*.la
%{yast_plugindir}/lib*.so
%{yast_plugindir}/lib*.la
%{yast_includedir}
%{_libdir}/pkgconfig/yast2-core.pc
%doc %{yast_docdir}
%doc %{_datadir}/doc/yastdoc
%{yast_ydatadir}/devtools/bin/generateYCPWrappers

%changelog
