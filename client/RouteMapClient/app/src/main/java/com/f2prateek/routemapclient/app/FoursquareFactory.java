package com.f2prateek.routemapclient.app;

import com.f2prateek.routemapclient.app.model.foursquare.VenuesResponse;
import com.f2prateek.routemapclient.app.model.server.PathResponse;
import com.f2prateek.routemapclient.app.model.server.ServerLocation;
import java.util.List;
import retrofit.Callback;
import retrofit.RestAdapter;
import retrofit.http.GET;
import retrofit.http.Query;

public class FoursquareFactory {

  private static Foursquare instance;

  private FoursquareFactory() {
    // no instances
  }

  public static Foursquare get() {
    if (instance == null) {
      RestAdapter restAdapter =
          new RestAdapter.Builder().setEndpoint("http://192.168.1.67:5000/api")
              .setLogLevel(RestAdapter.LogLevel.FULL)
              .build();
      instance = restAdapter.create(Foursquare.class);
    }
    return instance;
  }

  public interface Foursquare {
    @GET("/venues") void venues(@Query("location") ServerLocation serverLocation,
        Callback<VenuesResponse> cb);

    @GET("/route") void route(@Query("location") List<ServerLocation> serverLocation,
        Callback<PathResponse> cb);
  }
}
