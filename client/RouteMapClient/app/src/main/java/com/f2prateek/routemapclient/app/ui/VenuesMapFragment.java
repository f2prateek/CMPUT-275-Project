package com.f2prateek.routemapclient.app.ui;

import android.content.Context;
import android.location.Location;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.widget.Toast;
import com.f2prateek.ln.Ln;
import com.f2prateek.routemapclient.app.FoursquareFactory;
import com.f2prateek.routemapclient.app.R;
import com.f2prateek.routemapclient.app.model.foursquare.FoursquareVenue;
import com.f2prateek.routemapclient.app.model.foursquare.VenuesResponse;
import com.f2prateek.routemapclient.app.model.server.PathResponse;
import com.f2prateek.routemapclient.app.model.server.ServerLocation;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.MapFragment;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.PolylineOptions;
import com.google.maps.android.clustering.ClusterManager;
import com.google.maps.android.clustering.view.DefaultClusterRenderer;
import java.util.ArrayList;
import java.util.List;
import pl.charmas.android.reactivelocation.ReactiveLocationProvider;
import retrofit.Callback;
import retrofit.RetrofitError;
import retrofit.client.Response;
import rx.util.functions.Action1;

public class VenuesMapFragment extends MapFragment {

  ClusterManager<FoursquareVenue> venueClusterManager;
  ClusterManager<ServerLocation> routeClusterManager;
  Location lastKnownLocation;
  List<FoursquareVenue> selectedVenues = new ArrayList<FoursquareVenue>();

  @Override public void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    setHasOptionsMenu(true);
  }

  @Override public void onCreateOptionsMenu(Menu menu, MenuInflater inflater) {
    super.onCreateOptionsMenu(menu, inflater);
    inflater.inflate(R.menu.fragment_map, menu);
  }

  @Override public void onStart() {
    super.onStart();

    getMap().setMyLocationEnabled(true);
    getMap().setIndoorEnabled(true);
    getMap().getUiSettings().setAllGesturesEnabled(true);

    ReactiveLocationProvider locationProvider = new ReactiveLocationProvider(getActivity());
    locationProvider.getLastKnownLocation().subscribe(new Action1<Location>() {
      @Override
      public void call(Location location) {
        lastKnownLocation = location;
        centerMap(location);

        FoursquareFactory.get()
            .venues(new ServerLocation(location), new Callback<VenuesResponse>() {
              @Override public void success(VenuesResponse venuesResponse, Response response) {
                venueClusterManager = new ClusterManager<FoursquareVenue>(getActivity(), getMap());
                venueClusterManager.setRenderer(
                    new VenueRenderer(getActivity(), getMap(), venueClusterManager));

                getMap().setOnCameraChangeListener(venueClusterManager);
                getMap().setOnMarkerClickListener(venueClusterManager);

                venueClusterManager.addItems(venuesResponse.venues);
                venueClusterManager.cluster();
                venueClusterManager.setOnClusterItemClickListener(
                    new ClusterManager.OnClusterItemClickListener<FoursquareVenue>() {
                      @Override public boolean onClusterItemClick(FoursquareVenue foursquareVenue) {
                        if (selectedVenues.contains(foursquareVenue)) {
                          selectedVenues.remove(foursquareVenue);
                        } else {
                          selectedVenues.add(foursquareVenue);
                        }
                        return false;
                      }
                    }
                );
              }

              @Override public void failure(RetrofitError error) {
                Toast.makeText(getActivity(), "An unknown error occurred.", Toast.LENGTH_LONG)
                    .show();
              }
            });
      }
    });
  }

  private void centerMap(Location location) {
    LatLng moveTo = new LatLng(location.getLatitude(), location.getLongitude());
    getMap().animateCamera(CameraUpdateFactory.newLatLngZoom(moveTo, 10));
  }

  @Override public boolean onOptionsItemSelected(MenuItem item) {
    if (item.getItemId() == R.id.action_route) {
      List<ServerLocation> selectedLocations = new ArrayList<ServerLocation>();
      selectedLocations.add(new ServerLocation(lastKnownLocation));
      for (FoursquareVenue venue : selectedVenues) {
        selectedLocations.add(new ServerLocation(venue.location));
      }
      FoursquareFactory.get().route(selectedLocations, new Callback<PathResponse>() {
        @Override public void success(PathResponse pathResponse, Response response) {
          venueClusterManager.clearItems();
          getMap().clear();
          routeClusterManager = new ClusterManager<ServerLocation>(getActivity(), getMap());

          getMap().setOnCameraChangeListener(routeClusterManager);
          getMap().setOnMarkerClickListener(routeClusterManager);

          routeClusterManager.addItems(pathResponse.path);
          routeClusterManager.cluster();

          PolylineOptions polylineOptions = new PolylineOptions();
          for (ServerLocation location : pathResponse.path) {
            polylineOptions.add(location.getPosition());
          }
          getMap().addPolyline(polylineOptions);
          Toast.makeText(getActivity(), pathResponse.toString(), Toast.LENGTH_LONG).show();
        }

        @Override public void failure(RetrofitError error) {
          Ln.e(error.getCause());
          Toast.makeText(getActivity(), "An unknown error occurred.", Toast.LENGTH_LONG).show();
        }
      });
    }
    return super.onOptionsItemSelected(item);
  }

  static class VenueRenderer extends DefaultClusterRenderer<FoursquareVenue> {
    public VenueRenderer(Context context, GoogleMap map,
        ClusterManager<FoursquareVenue> clusterManager) {
      super(context, map, clusterManager);
    }

    @Override
    protected void onBeforeClusterItemRendered(FoursquareVenue venue, MarkerOptions markerOptions) {
      markerOptions.icon(BitmapDescriptorFactory.fromResource(R.drawable.ic_location_marker))
          .title(venue.name);
    }
  }
}
