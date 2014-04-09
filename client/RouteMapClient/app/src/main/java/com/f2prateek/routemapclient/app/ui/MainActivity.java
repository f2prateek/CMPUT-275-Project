package com.f2prateek.routemapclient.app.ui;

import android.app.Activity;
import android.os.Bundle;

public class MainActivity extends Activity {

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    if (savedInstanceState == null) {
      VenuesMapFragment fragment = new VenuesMapFragment();
      getFragmentManager().beginTransaction().add(android.R.id.content, fragment).commit();
    }
  }
}
