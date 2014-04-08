#!/usr/bin/env perl
# -*- cperl -*-
=head1 NAME

=head1 SYNOPSYS

 RCS:$Id$

=head1 DESCRIPTION

=head1 HISTORY

 ORIGIN: created from templateApp.pl version 3.4 by Min-Yen Kan <kanmy@comp.nus.edu.sg>

 RCS:$Log$

=cut
require 5.0;
use Getopt::Std;
# use diagnostics;

### USER customizable section
my $tmpfile .= $0; $tmpfile =~ s/[\.\/]//g;
$tmpfile .= $$ . time;
if ($tmpfile =~ /^([-\@\w.]+)$/) { $tmpfile = $1; }           # untaint tmpfile variable
$tmpfile = "/tmp/" . $tmpfile;
$0 =~ /([^\/]+)$/; my $progname = $1;
my $outputVersion = "1.0";
### END user customizable section

### Ctrl-C handler
sub quitHandler {
  print STDERR "\n# $progname fatal\t\tReceived a 'SIGINT'\n# $progname - exiting cleanly\n";
  exit;
}

### HELP Sub-procedure
sub Help {
  print STDERR "usage: $progname -h\t\t\t\t[invokes help]\n";
  print STDERR "       $progname -v\t\t\t\t[invokes version]\n";
  print STDERR "       $progname [-q] filename(s)...\n";
  print STDERR "Options:\n";
  print STDERR "\t-q\tQuiet Mode (don't echo license)\n";
  print STDERR "\n";
  print STDERR "Will accept input on STDIN as a single file.\n";
  print STDERR "\n";
}

### VERSION Sub-procedure
sub Version {
  if (system ("perldoc $0")) {
    die "Need \"perldoc\" in PATH to print version information";
  }
  exit;
}

sub License {
  print STDERR "# Copyright 2006 \251 by Min-Yen Kan\n";
}

###
### MAIN program
###

my $cmdLine = $0 . " " . join (" ", @ARGV);
if ($#ARGV == -1) {                 # invoked with no arguments, possible error in execution? 
  print STDERR "# $progname info\t\tNo arguments detected, waiting for input on command line.\n";  
  print STDERR "# $progname info\t\tIf you need help, stop this program and reinvoke with \"-h\".\n";
}

$SIG{'INT'} = 'quitHandler';
getopts ('hl:qv');

our ($opt_l, $opt_q, $opt_v, $opt_h);
# use (!defined $opt_X) for options with arguments
if (!$opt_q) { License(); }     # call License, if asked for
if ($opt_v) { Version(); exit(0); } # call Version, if asked for
if ($opt_h) { Help(); exit (0); }   # call help, if asked for

## standardize input stream (either STDIN on first arg on command line)
my $fh; my $fh2; my $fh3;
my $filename;

## standardize input stream (either STDIN on first arg on command line)
my $fh;
my $filename;
$filename = shift;
if (!(-e $filename)) { die "# $progname crash\t\tFile \"$filename\" doesn't exist"; }
open (*IF, $filename) || die "# $progname crash\t\tCan't open \"$filename\"";
$fh = "IF";

## process system's answer
my $sys;
while (<$fh>) {
  chop;
  $sys = $_;
}
close ($fh);
my @sys = split (/ +/,$sys);

## process gold answer
$filename = shift;
if (!(-e $filename)) { die "# $progname crash\t\tFile \"$filename\" doesn't exist"; }
open (*IF, $filename) || die "# $progname crash\t\tCan't open \"$filename\"";
$fh = "IF";

my %qrel = ();
my $totalPositive = 0;
while (<$fh>) {
  chop;
  my ($file,$judgment) = split(/\t/,$_);
  if ($judgment == 1) {     # 1's are positive judgments, 0's negative, -1 unknowns
    $totalPositive++;
  }
  @qrel{$file} = $judgment;
}
close ($fh);

# compare
my $count = 0;
my $unknown = 0;
my $correct = 0;
my $beta = 2.0;
my @precision = ();
my @recall = ();
my @f = ();
my $sumP = 0;
my $sumR = 0;
my $sumF = 0;
my $f = 0;
for (my $i = 0; $i <= $#sys; $i++) {
  $count++;
  my $file = $sys[$i];
  my $judge = (defined $qrel{$file}) ? $qrel{$file} : -1;
  if ($judge == 1) {
    $correct++;
  } elsif ($judge == -1) {
    $unknown++;
    next;
  } else {          # incorrect
    ;
  }

  push (@precision, ($count-$unknown == 0) ? 0 : $correct/($count-$unknown));
  push (@recall, ($count-$unknown == 0) ? 0 : $correct/$totalPositive);
  $f = (((($beta * $beta * $precision[$#precision])+$recall[$#recall]) == 0) ? 0 : 
    (((($beta*$beta)+1)*$precision[$#precision]*$recall[$#recall])/((($beta * $beta) * $precision[$#precision])+$recall[$#recall]))
    );
  push (@f, $f);

  $sumP += $precision[$#f];
  $sumR += $recall[$#f];
  $sumF += $f[$#f];

#  print "$count ($file: $judge): P: $precision[$#precision] R: $recall[$#recall] ($totalPositive) F: $f[$#f] Sums: $sumP $sumR $sumF\n";
}

my $avgP = (($#f + 1) == 0) ? 0 :$sumP/($#f + 1);
my $avgR = (($#f + 1) == 0) ? 0 :$sumR/($#f + 1);
my $avgF = (($#f + 1) == 0) ? 0 :$sumF/($#f + 1);

#print "Sum F: $sumF\nSum Precision: $sumP\nSum Recall: $sumR\n";
print "Average F: $avgF\nAverage Precision: $avgP\nAverage Recall: $avgR\nCount: $count\nCorrect: $correct\nPoints Judged: ",  ($#precision + 1), "\n";