# https://fedoraproject.org/wiki/Packaging:Guidelines#Compiler_flags
%define _hardened_build 1

Name:               lldpad
Version:            0.9.46
Release:            10%{?dist}
Summary:            Intel LLDP Agent
Group:              System Environment/Daemons
License:            GPLv2
URL:                http://open-lldp.org/
Source0:            %{name}-%{version}.tar.gz
Patch0:             %{name}-%{version}-123-g48a5f38.patch
Patch1:             %{name}-0.9.46-Ignore-supplied-PG-configuration-if-PG-is-being-disabled.patch
Requires:           kernel >= 2.6.32
BuildRequires:      automake autoconf libtool
BuildRequires:      flex >= 2.5.33
BuildRequires:      kernel-headers >= 2.6.32
BuildRequires:      libconfig-devel >= 1.3.2
BuildRequires:      libnl3-devel
BuildRequires:      readline-devel
BuildRequires:      systemd
Requires:           readline
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
Provides:           dcbd = %{version}-%{release}
Obsoletes:          dcbd < 0.9.26

%description
This package contains the Linux user space daemon and configuration tool for
Intel LLDP Agent with Enhanced Ethernet support for the Data Center.

%package            devel
Summary:            Development files for %{name}
Group:              Development/Libraries
Requires:           %{name}%{?_isa} = %{version}-%{release}
Provides:           dcbd-devel = %{version}-%{release}
Obsoletes:          dcbd-devel < 0.9.26

%description devel
The %{name}-devel package contains header files for developing applications
that use %{name}.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
./bootstrap.sh
%configure --disable-static
# fix the hardened build flags
sed -i -e 's! \\\$compiler_flags !&\\\$CFLAGS \\\$LDFLAGS !' libtool
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{_sharedstatedir}/%{name}
rm -f %{buildroot}%{_libdir}/liblldp_clif.la

%post
/sbin/ldconfig
%systemd_post %{name}.service %{name}.socket

%preun
%systemd_preun %{name}.service %{name}.socket

%postun
/sbin/ldconfig
%systemd_postun_with_restart %{name}.service %{name}.socket

%post devel
## provide legacy support for apps that use the old dcbd interface.
if [ ! -e %{_includedir}/dcbd ]; then
    ln -T -s %{_includedir}/lldpad %{_includedir}/dcbd
fi
if [ ! -e %{_includedir}/dcbd/clif_cmds.h ]; then
    ln -T -s %{_includedir}/lldpad/lldp_dcbx_cmds.h %{_includedir}/dcbd/clif_cmds.h
fi

%preun devel
if [ -e %{_includedir}/dcbd/clif_cmds.h ]; then
    rm -f %{_includedir}/dcbd/clif_cmds.h
fi
if [ -e %{_includedir}/dcbd ]; then
    rm -f %{_includedir}/dcbd
fi

%files
%doc COPYING README ChangeLog
%{_sbindir}/*
%{_libdir}/liblldp_clif.so.*
%dir %{_sharedstatedir}/%{name}
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}.socket
%dir %{_sysconfdir}/bash_completion.d/
%{_sysconfdir}/bash_completion.d/*
%{_mandir}/man8/*

%files devel
%{_includedir}/*
%{_libdir}/pkgconfig/*.pc
%{_libdir}/liblldp_clif.so

%changelog
* Tue Oct 21 2014 Chris Leech <cleech@redhat.com> - 0.9.46-10
- Sync with upstream v0.9.46-123-g48a5f38 (#1087096)

* Fri Jun 27 2014 Chris Leech <cleech@redhat.com> - 0.9.46-9
- Fix IEEE mode DCBX (#1102886)

* Wed Mar 19 2014 Petr Šabata <contyk@redhat.com> - 0.9.46-8
- Ignore supplied PG configuration if PG is being disabled (#1067261)

* Tue Mar 18 2014 Petr Šabata <contyk@redhat.com> - 0.9.46-7
- Migrate properly with VEPA (#1070725)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 0.9.46-6
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.9.46-5
- Mass rebuild 2013-12-27

* Fri Nov 08 2013 Petr Šabata <contyk@redhat.com> - 0.9.46-4
- Support multiple virtual machines again (#1020625)

* Wed Jul 31 2013 Petr Šabata <contyk@redhat.com> - 0.9.46-3
- Require 'systemd' instead of 'systemd-units'

* Tue Jul 02 2013 Petr Šabata <contyk@redhat.com> - 0.9.46-2
- Fix the hardened build flags

* Tue Jun 04 2013 Petr Šabata <contyk@redhat.com> - 0.9.46-1
- 0.9.46 bump
- 802.1Qaz fixes to enable support on not CEE DCBX-enabled hardware
- 802.1Qbg EVB module support
- lldpad now supports bonded interfaces

* Tue Mar 05 2013 Petr Šabata <contyk@redhat.com> - 0.9.45-5
- Fix build by patching the sizeof() call in lldp_8021qaz_cmds.c

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.45-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Aug 28 2012 Petr Šabata <contyk@redhat.com> - 0.9.45-3
- Migrate to systemd scriptlets (#850192)

* Thu Aug 23 2012 Petr Šabata <contyk@redhat.com> - 0.9.45-2
- Fix displaying of the Management Address TLV (327ef662)

* Wed Aug 15 2012 Petr Šabata <contyk@redhat.com> - 0.9.45-1
- 0.9.45 bump
- Provide bash-completion and the new clif library

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.44-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 27 2012 Petr Šabata <contyk@redhat.com> - 0.9.44-1
- 0.9.44 bump, patches cleanup
- Correct dependencies a bit
- Require dlopen()'d readline

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.43-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Oct 06 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-5
- Do not enable lldpad by default (#701999)

* Fri Sep 23 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-4
- Enable hardened build

* Tue Sep 13 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-3
- Mute systemd output (#737897)

* Tue Aug 30 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-2
- Apply various upstream 0.9.43 bugfixes
- Include not yet accepted Jens Osterkamp's patch to fix bug #720080
- Whitespace cleanup, phew

* Thu Jul 07 2011 Petr Sabata <contyk@redhat.com> - 0.9.43-1
- 0.9.43 bump
- Drop the the clean exit patch and our unit file, both are now included upstream

* Tue Jun 21 2011 Petr Sabata <contyk@redhat.com> - 0.9.42-2
- Introduce systemd unit file, drop SysV support
- Call systemctl instead of service and chkconfig
- Enable the service only on new installation (post)
- Clean exit patch

* Mon Jun 13 2011 Petr Sabata <contyk@redhat.com> - 0.9.42-1
- 0.9.42 bump (massive patches cleanup)
- Remove obsolete defattr
- Remove COPYING and README from devel subpackage

* Wed May  4 2011 Petr Sabata <psabata@redhat.com> - 0.9.41-3
- Fix the frequent, power consuming lldpad wake-ups (rhbz#701943)

* Thu Apr 21 2011 Petr Sabata <psabata@redhat.com> - 0.9.41-2
- Bring in upstream 802.1Qbg bugfixes

* Thu Feb 10 2011 Petr Sabata <psabata@redhat.com> - 0.9.41-1
- 0.9.41 bump
- New BR: autotools, flex
- Buildroot garbage removed
- Devel post and preun scriptlets sanitized

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.38-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jun 28 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.38-1
- rebased to 0.9.38 (various enhancements and bugfixes, see 
  lldpad-0.9.38-relnotes.txt on http://e1000.sf.net for complete list)

* Mon May 10 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.32-2
- rebuild to match new libconfig

* Mon Apr 12 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.32-1
- rebased to 0.9.32 (various enhancements and bugfixes, see 
  lldpad-0.9.32-relnotes.txt on http://e1000.sf.net for complete list)

* Thu Mar 25 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.29-2
- added Provides and Obsoletes tags to devel subpackage

* Mon Mar 15 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.29-1
- updated package to 0.9.29, improved compatibility with fcoe-utils

* Fri Feb 26 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.26-2
- updated spec file and LSB init script patch for re-review
  (#568641)

* Thu Feb 25 2010 Jan Zeleny <jzeleny@redhat.com> - 0.9.26-1
- rebased to 0.9.26
- package renamed to lldpad
- enahanced functionality (LLDP supported as well as DCBX)

* Fri Nov 13 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.19-2
- init script patch adding LSB compliance

* Thu Oct 08 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.19-1
- update to new upstream version

* Mon Oct 05 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.15-5
- replaced the last patch, which was not fully functional, with
  the new one

* Wed Sep 09 2009 Karsten Hopp <karsten@redhat.com> 0.9.15-4
- buildrequire libconfig-devel >= 1.3.2, it doesn't build with 1.3.1 due to
  the different config_lookup_string api

* Thu Aug 20 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.15-3
- update of config_lookup_string() function calls

* Thu Aug 20 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.15-2
- rebuild in order to match new libconfig

* Mon Aug 17 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.15-1
- rebase to 0.9.15

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Mar 20 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.7-4
- updated scriptlets in spec file to follow the rules

* Wed Mar 11 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.7-3
- added devel files again to support fcoe-utils package
- added kernel >= 2.6.29 to Requires, deleted dcbnl.h, since it is
  aviable in kernel 2.6.29-rc7
- changed config dir from /etc/sysconfig/dcbd to /etc/dcbd
- updated init script: added mandatory Short description tag,
  deleted default runlevels, which should start the script

* Tue Mar 10 2009 Jan Zeleny <jzeleny@redhat.com> - 0.9.7-2
- added patch to enable usage of libconfig shared in system
- removed devel part of package

* Mon Mar 2 2009 Chris Leech <christopher.leech@intel.com> - 0.9.7-1
- Updated to 0.9.7
- Added a private copy of dcbnl.h until kernel-headers includes it.
  Export patch is making it's way to the upstream kernel via net-2.6,
  expected in 2.6.29-rc7

* Thu Feb 26 2009 Chris Leech <christopher.leech@intel.com> - 0.9.5-1
- initial RPM packaging
