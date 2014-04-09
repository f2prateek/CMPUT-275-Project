/*
 * Copyright 2014 Prateek Srivastava (@f2prateek)
 *
 *    Licensed under the Apache License, Version 2.0 (the "License");
 *    you may not use this file except in compliance with the License.
 *    You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *    Unless required by applicable law or agreed to in writing, software
 *    distributed under the License is distributed on an "AS IS" BASIS,
 *    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *    See the License for the specific language governing permissions and
 *    limitations under the License.
 */

package com.f2prateek.routemapclient.app.model.server;

import com.google.android.gms.maps.model.LatLng;
import com.google.maps.android.clustering.ClusterItem;

public class ServerLocation implements ClusterItem {
  public double lat;
  public double lng;

  public ServerLocation(double lat, double lng) {
    this.lat = lat;
    this.lng = lng;
  }

  public ServerLocation(android.location.Location location) {
    this.lat = location.getLatitude();
    this.lng = location.getLongitude();
  }

  public ServerLocation(com.f2prateek.routemapclient.app.model.foursquare.Location location) {
    this.lat = location.lat;
    this.lng = location.lng;
  }

  @Override public String toString() {
    return "(" + lat + ',' + lng + ')';
  }

  @Override public LatLng getPosition() {
    return new LatLng(lat, lng);
  }
}