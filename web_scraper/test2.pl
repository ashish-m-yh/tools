use Mojo::UserAgent;
use Mojo::DOM;
use Set::CrossProduct;
use Data::Dumper;

my $data = `cat ./conf.xml`;

my $dom = Mojo::DOM->new($data, 'xml' => 1);
my $ua = Mojo::UserAgent->new;

my %mem;

foreach my $e ($dom->find('step')->each) {
	my $url = $e->at('url')->text;

	my $tuples;

	if ($url =~ /\$/) {
		my @vars = $url =~ /_\$(.*)_/sg;

		print $url;

		my $ref = [];

		foreach (@vars) {
			if (exists $mem{$_}) {
				push @$ref, $mem{$_};
			}
		}

		if (@vars > 1) {
			my $iterator = Set::CrossProduct->new($ref);
			my $tuples   = $iterator->combinations;

		}
		else {

		}

		print Data::Dumper->Dump([ $tuples ]);
	}


	eval {
		my $dom = $ua->get($url)->res->dom;	
		my $match = $e->at('match_path')->text;
		my @paths = map { $_->text } $e->find('extract_to_field')->each;

		if ($match && @paths) {
			foreach my $e ($dom->find($match)->each) {
				foreach my $path (@paths) {
					my ($field,$dom_path,$att) = split(/:/,$path);

					if ($att) {
						$val = $e->attrs($att);
					}	
					elsif ($dom_path =~ /^\@(.*)/) {
						$val = $e->attrs($1);
					}
					else {
						$val = $e->text;
					} 

					push @{$mem{$field}}, $val if ($val ne '');
				}	
			}
		}
	};
}
