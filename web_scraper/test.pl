use Mojo::UserAgent;
use LWP::Simple;
use Data::Dumper;

# Fresh user agent
  my $ua = Mojo::UserAgent->new;
	
  my $city_url = "http://www.snapdeal.com/";
  my $dom      =  $ua->get($city_url)->res->dom; 

  foreach my $e ($dom->find('option[pageurl]')->each) {
	  my $city = $e->attrs('pageurl'); 

	  if ($city) {
		  my $dom2 = $ua->get($city_url."/deals-$city?systemcode=501&loginSuccess=success")->res->dom;

		  foreach my $deal ($dom2->find('div[class=content-placeholder]')->each) {
			  foreach my $e ($deal->find('[class=deal-title]')->each) {
				  print $e->text."\n";
			  }

			  foreach my $e ($deal->find('a[class=buylink]')->each) {
				  print $e->attrs('href')."\n";
			  }
		  }
	  }
  }
