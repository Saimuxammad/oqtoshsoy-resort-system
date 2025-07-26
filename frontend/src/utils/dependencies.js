export async function get_current_user() {
  return {
    id: 1,
    telegram_id: 123456789,
    first_name: "Test",
    last_name: "User",
    username: "testuser",
    is_admin: true
  };
}